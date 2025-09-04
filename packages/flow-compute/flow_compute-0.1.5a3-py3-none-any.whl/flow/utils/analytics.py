"""Minimal async analytics sink (Amplitude-compatible).

Centralizes optional remote analytics delivery for the CLI and adapters.
Best-effort and completely optional. Configuration is read from client-side
files under ``~/.flow`` with environment variable overrides for advanced
use-cases (e.g., CI).

Design goals:
- Zero user-facing latency or failures (no exceptions raised)
- Opt-in only (see telemetry_enabled) and privacy-conscious payloads
- Safe-by-default timeouts and batching

- Enabled only when telemetry is opted in via settings
- Sends non-blocking, batched events to Amplitude's HTTP API
- Never raises or logs noisy errors; silently drops on failures
- Uses a stable, anonymous device_id stored under ~/.flow/analytics_id

Configuration precedence (highest first):
1) Environment variables (when set):
   - FLOW_TELEMETRY: "1"/true to enable local+remote telemetry
   - FLOW_AMPLITUDE_API_KEY: Amplitude project API key
   - FLOW_AMPLITUDE_URL: override ingestion URL
2) File: ~/.flow/telemetry.yaml (preferred)
3) File: ~/.flow/config.yaml (fallback under telemetry: ...)
"""

from __future__ import annotations

import atexit
import contextlib
import os
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Final

_requests: ModuleType | None = None
try:  # requests is already a dependency in this project
    import requests as _req
    _requests = _req
except Exception:  # pragma: no cover - extremely defensive  # noqa: BLE001
    _requests = None


DEFAULT_INGEST_URL: Final[str] = "https://api2.amplitude.com/2/httpapi"
# Tunables for batching and timeouts (kept small to avoid blocking UX)
BATCH_MAX: Final[int] = 20
BATCH_INTERVAL_SECONDS: Final[float] = 1.0
REQUEST_TIMEOUT_SECONDS: Final[float] = 0.75
FINAL_DRAIN_TIMEOUT_SECONDS: Final[float] = 0.50

# ---- settings loader (shared) -------------------------------------------------

def _read_yaml(path: Path) -> dict[str, Any]:
    """Best-effort YAML reader that returns a dict or {}."""
    try:
        if not path.exists():
            return {}
        import yaml  # local import to avoid global import cost

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001 - best-effort config parse
        return {}


def _boolish(v: Any) -> bool:
    """Return True if value represents a truthy flag (1/true/yes/on)."""
    try:
        s = str(v).strip().lower()
        return s in {"1", "true", "yes", "on"}  # noqa: TRY300
    except Exception:  # noqa: BLE001 - defensive conversion
        return False


def _load_telemetry_settings() -> dict[str, Any]:  # noqa: C901 - config loader favors clarity over refactors
    """Load telemetry settings with env overrides.

    Returns a dict with keys:
      - enabled: bool
      - amplitude: { api_key: str | "", url: str }
    """
    base: dict[str, Any] = {"enabled": False, "amplitude": {"api_key": "", "url": DEFAULT_INGEST_URL}}

    home = Path.home() / ".flow"
    telem_path = home / "telemetry.yaml"
    config_path = home / "config.yaml"

    data = _read_yaml(telem_path)
    if not data:
        # fallback to config.yaml under telemetry
        cfg = _read_yaml(config_path)
        if isinstance(cfg.get("telemetry"), dict):
            data = cfg.get("telemetry", {})

    if isinstance(data, dict):
        try:
            enabled = data.get("enabled")
            if enabled is not None:
                base["enabled"] = bool(enabled) if isinstance(enabled, bool) else _boolish(enabled)
            amp = data.get("amplitude") or {}
            if isinstance(amp, dict):
                if isinstance(amp.get("api_key"), str):
                    base["amplitude"]["api_key"] = amp.get("api_key")
                if isinstance(amp.get("url"), str) and amp.get("url"):
                    base["amplitude"]["url"] = amp.get("url")
        except Exception:  # noqa: BLE001 - tolerant of malformed settings
            pass

    # env overrides (opt-in for CI/advanced usage)
    try:
        env_enabled = os.environ.get("FLOW_TELEMETRY")
        if env_enabled is not None and str(env_enabled).strip() != "":
            base["enabled"] = _boolish(env_enabled)
    except Exception:  # noqa: BLE001 - environment access is best-effort
        pass
    try:
        env_key = os.environ.get("FLOW_AMPLITUDE_API_KEY")
        if env_key is not None and str(env_key).strip() != "":
            base["amplitude"]["api_key"] = str(env_key)
    except Exception:  # noqa: BLE001 - environment access is best-effort
        pass
    try:
        env_url = os.environ.get("FLOW_AMPLITUDE_URL")
        if env_url is not None and str(env_url).strip() != "":
            base["amplitude"]["url"] = str(env_url)
    except Exception:  # noqa: BLE001 - environment access is best-effort
        pass

    return base


def telemetry_enabled() -> bool:
    """Return True when telemetry is enabled by settings/env.

    Used by CLI/adapters telemetry wrappers to gate local JSONL logging too.
    """
    try:
        settings = _load_telemetry_settings()
        return bool(settings.get("enabled"))
    except Exception:  # noqa: BLE001 - guard callers from telemetry failures
        return False


def _get_flow_version() -> str:
    try:
        from flow._version import get_version  # local import to avoid early import cost

        return get_version()
    except Exception:  # noqa: BLE001 - version lookup is best-effort
        return "0.0.0+unknown"


def _get_device_id() -> str:
    """Return a stable, anonymous device id (persisted locally)."""
    try:
        path = Path.home() / ".flow" / "analytics_id"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = path.read_text(encoding="utf-8").strip()
            if data:
                return data
        # Generate and persist a new UUIDv4 string
        import uuid

        new_id = str(uuid.uuid4())
        path.write_text(new_id, encoding="utf-8")
        # Best-effort POSIX permission hardening
        try:
            if os.name == "posix":
                os.chmod(path, 0o600)
        except Exception:  # noqa: BLE001 - permission hardening is best-effort
            pass
        return new_id  # noqa: TRY300
    except Exception:  # noqa: BLE001 - last-resort fallback
        # Worst case, return a volatile identifier for this process
        return f"ephemeral-{int(time.time())}"


@dataclass
class AnalyticsEvent:
    event_type: str
    event_properties: dict[str, Any]
    time_ms: int | None = None
    insert_id: str | None = None


class _AmplitudeWorker:
    """Background worker that batches and ships events to Amplitude."""

    def __init__(self) -> None:
        self._queue: queue.Queue[AnalyticsEvent] = queue.Queue(maxsize=1024)
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._device_id = _get_device_id()
        self._app_version = _get_flow_version()
        # Hidden debug knob for local troubleshooting; not part of public API
        self._debug = os.environ.get("FLOW_TELEMETRY_DEBUG") == "1"

    def enabled(self) -> bool:
        try:
            if _requests is None:
                return False
            settings = _load_telemetry_settings()
            if not bool(settings.get("enabled")):
                return False
            api_key = str(settings.get("amplitude", {}).get("api_key") or "")
            return api_key.strip() != ""
        except Exception:  # noqa: BLE001 - do not leak telemetry exceptions
            return False

    def start(self) -> None:
        if not self.enabled() or self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name="flow-amplitude", daemon=True)
        self._thread.start()
        atexit.register(self.stop)

    def enqueue(self, event: AnalyticsEvent) -> None:
        if not self.enabled():
            return
        with contextlib.suppress(Exception):
            self._queue.put_nowait(event)

    def flush(self) -> None:
        """Best-effort wait for the queue to drain for up to ~1s."""
        if not self.enabled():
            return
        deadline = time.time() + 1.0
        while not self._queue.empty() and time.time() < deadline:
            time.sleep(0.02)

    def stop(self) -> None:
        """Signal the worker to stop and perform a final drain.

        Does not join the daemon thread to avoid shutdown delays.
        """
        try:
            if not self.enabled():
                return
            self._stop.set()
            self.flush()
        except Exception:  # noqa: BLE001 - safe shutdown best-effort
            pass

    # --- internal ---
    def _run(self) -> None:
        settings = _load_telemetry_settings()
        url = str(settings.get("amplitude", {}).get("url") or DEFAULT_INGEST_URL)
        # Enforce HTTPS to avoid accidental http:// misconfigurations
        if not url.startswith("https://"):
            url = DEFAULT_INGEST_URL
        api_key = str(settings.get("amplitude", {}).get("api_key") or "").strip()
        session = None
        if _requests is not None:
            try:
                session = _requests.Session()
            except Exception:  # noqa: BLE001 - best-effort session creation
                session = None

        batch: list[dict[str, Any]] = []
        last_send = time.time()
        try:
            while not self._stop.is_set():
                # Batch up to N events or every T seconds
                try:
                    ev = self._queue.get(timeout=0.25)
                    batch.append(self._to_amplitude(ev))
                except queue.Empty:
                    pass

                now = time.time()
                if batch and (len(batch) >= BATCH_MAX or (now - last_send) > BATCH_INTERVAL_SECONDS):
                    self._send(session, url, api_key, batch)
                    batch = []
                    last_send = now

            # Drain remaining events on stop
            if batch:
                self._send(session, url, api_key, batch, timeout=FINAL_DRAIN_TIMEOUT_SECONDS)
        finally:
            try:
                if session is not None:
                    session.close()
            except Exception:  # noqa: BLE001 - ignore session close failures
                pass

    def _to_amplitude(self, ev: AnalyticsEvent) -> dict[str, Any]:
        t_ms = ev.time_ms if isinstance(ev.time_ms, int) else int(time.time() * 1000)
        # Minimal, privacy-conscious envelope
        out = {
            "event_type": ev.event_type,
            "time": t_ms,
            "device_id": self._device_id,
            "event_properties": ev.event_properties,
            "app_version": self._app_version,
            "platform": "python",
        }
        # Recommended for de-duplication within (device_id, insert_id)
        try:
            if not ev.insert_id:
                import uuid

                ev.insert_id = str(uuid.uuid4())
            out["insert_id"] = ev.insert_id
        except Exception:  # noqa: BLE001 - insert_id generation failure ignored
            pass
        # Add a small amount of contextual metadata safely
        try:
            import platform
            import sys

            out["os_name"] = platform.system()
            out["os_version"] = platform.version()[:64]
            out["python"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        except Exception:  # noqa: BLE001 - platform probing is best-effort
            pass
        return out

    def _send(
        self,
        session: Any,
        url: str,
        api_key: str,
        events: list[dict[str, Any]],
        *,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
    ) -> None:
        """Send one batch, with a tiny retry on transient 429/5xx.

        Best-effort only; drops on failures without raising.
        """
        if not events:
            return
        payload = {"api_key": api_key, "events": events}
        try:
            if session is not None:
                resp = session.post(url, json=payload, timeout=timeout)
            else:
                if _requests is None:
                    return
                resp = _requests.post(url, json=payload, timeout=timeout)
            code = getattr(resp, "status_code", 0)
            if code in (429, 500, 502, 503, 504):
                # One small backoff retry to smooth out transient errors
                time.sleep(0.1)
                if session is not None:
                    session.post(url, json=payload, timeout=timeout)
                elif _requests is not None:
                    _requests.post(url, json=payload, timeout=timeout)
        except Exception:  # noqa: BLE001 - drop on failure; never raise
            # Drop on failure; never raise
            pass


_worker = _AmplitudeWorker()


def start() -> None:
    """Start the background worker (no-op if already started/disabled)."""
    with contextlib.suppress(Exception):
        _worker.start()


def track(event_type: str, properties: dict[str, Any] | None = None, *, time_ms: int | None = None) -> None:
    """Enqueue an analytics event for async delivery.

    Does nothing unless both FLOW_TELEMETRY=1 and FLOW_AMPLITUDE_API_KEY are set.
    """
    try:
        if not _worker.enabled():
            return
        start()
        _worker.enqueue(
            AnalyticsEvent(event_type=event_type, event_properties=properties or {}, time_ms=time_ms)
        )
    except Exception:  # noqa: BLE001 - never raise from track
        pass
