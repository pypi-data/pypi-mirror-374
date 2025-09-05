"""Setup helpers for status command pre-execution concerns."""

from __future__ import annotations

import os


def apply_project_env(project: str | None) -> None:
    """If provided, set project env vars before creating Flow().

    The provider context resolves the project from ``MITHRIL_PROJECT_ID``.
    Set that primary variable, and also set legacy ``MITHRIL_PROJECT`` for
    downstream helpers that still read it.
    """
    if not project:
        return
    try:
        # Primary env used by provider context
        os.environ["MITHRIL_PROJECT_ID"] = project
        # Legacy alias used by some CLI helpers
        os.environ["MITHRIL_PROJECT"] = project
    except Exception:
        pass


def apply_force_refresh() -> None:
    """Clear prefetch caches before proceeding when --force-refresh is set."""
    try:
        from flow.cli.utils.prefetch import (
            refresh_active_task_caches as _refresh_active,
        )
        from flow.cli.utils.prefetch import (
            refresh_all_tasks_cache as _refresh_all,
        )

        _refresh_active()
        _refresh_all()
    except Exception:
        pass
