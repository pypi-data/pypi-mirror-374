"""Task query service for Mithril provider.

Encapsulates listing and pagination logic for tasks (bids), including
cursor-based pagination, deduplication, and light status filtering.
"""

from __future__ import annotations

import logging
import os
import random
import time
from typing import Any

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.domain.tasks import TaskService
from flow.sdk.models import Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskQueryService:
    def __init__(
        self,
        api: MithrilApiClient,
        task_service: TaskService,
        get_project_id: callable,
    ) -> None:
        self._api = api
        self._task_service = task_service
        self._get_project_id = get_project_id

    def list_tasks(
        self,
        status: TaskStatus | list[TaskStatus] | None = None,
        limit: int = 100,
        *,
        force_refresh: bool = False,
    ) -> list[Task]:
        """List tasks newest-first with pagination and deduplication."""

        # Map Flow TaskStatus to Mithril bid status filter values used by the API (v2).
        # Per OpenAPI `/v2/spot/bids` the allowed query values are:
        #   status ∈ {"Open", "Allocated", "Preempting", "Terminated", "Paused"}
        # We collapse Flow's terminal states into "Terminated" for filtering purposes.
        status_map = {
            TaskStatus.PENDING: "Open",
            TaskStatus.RUNNING: "Allocated",
            TaskStatus.PREEMPTING: "Preempting",
            TaskStatus.PAUSED: "Paused",
            TaskStatus.COMPLETED: "Terminated",
            TaskStatus.FAILED: "Terminated",
            TaskStatus.CANCELLED: "Terminated",
        }

        requested_statuses: list[str] | None
        if status is None:
            requested_statuses = None
        elif isinstance(status, list):
            mapped = [status_map.get(s) for s in status if s in status_map]
            requested_statuses = sorted({s for s in mapped if s})  # type: ignore[arg-type]
        else:
            mith = status_map.get(status)
            requested_statuses = [mith] if mith else None

        try:
            if os.environ.get("FLOW_STATUS_DEBUG"):
                pid = self._get_project_id()
                logging.getLogger("flow.status.provider").info(
                    f"mithril.task_query.list_tasks: project_id={pid} statuses={requested_statuses} limit={limit} force_refresh={force_refresh}"
                )
        except Exception:
            pass

        seen_task_ids: set[str] = set()
        unique_tasks: list[Task] = []
        page_count = 0
        max_pages = 10
        api_time = 0.0
        build_time = 0.0

        def _fetch_page(params: dict) -> tuple[list[dict], str | None, float]:
            """Fetch a page of bids with safe fallbacks for param compatibility.

            If the API rejects our params with a 422 (validation), retry with a
            reduced set of parameters to avoid noisy errors (e.g., drop status/sort).
            """
            start_api = time.time()
            try:
                response = self._api.list_bids(params)
            except Exception as e:
                # Retry on validation errors with minimal params: project, limit, next_cursor
                try:
                    from flow.errors import ValidationAPIError  # local import

                    if isinstance(e, ValidationAPIError):
                        minimal = {
                            k: v
                            for k, v in params.items()
                            if k in {"project", "limit", "next_cursor"}
                        }
                        response = self._api.list_bids(minimal)
                    else:
                        raise
                except Exception:
                    raise
            elapsed = time.time() - start_api
            # Support both dict responses (with pagination) and raw list responses
            if isinstance(response, list):
                bids = response
                next_cur = None
            else:
                bids = response.get("data", [])
                next_cur = response.get("next_cursor")
            return bids, next_cur, elapsed

        status_groups = requested_statuses or [None]
        for status_group in status_groups:
            next_cursor = None
            last_cursor = None
            pages_remaining = max_pages
            attempted_without_status = False  # fallback when server-side filter yields nothing

            while pages_remaining > 0 and len(unique_tasks) < limit * 2:
                pages_remaining -= 1
                page_count += 1
                params: dict[str, Any] = {
                    "project": self._get_project_id(),
                    "limit": 100,
                    # Request newest-first so active/recent tasks appear early.
                    # Aligns with single-task lookups which already use this ordering.
                    "sort_by": "created_at",
                    "sort_dir": "desc",
                }
                if status_group:
                    params["status"] = status_group
                if next_cursor:
                    # Use API-consistent pagination parameter name
                    params["next_cursor"] = next_cursor
                if force_refresh:
                    params["_cache_bust"] = f"{int(time.time())}-{random.randint(1000, 9999)}"

                bids, next_cursor_val, elapsed = _fetch_page(params)
                # Fallback: some API deployments accept the 'status' param but
                # return 0 rows. If the first page is empty, retry without the
                # server-side status filter and filter client-side instead.
                if not bids and status_group and not attempted_without_status and not next_cursor:
                    minimal = {k: v for k, v in params.items() if k != "status"}
                    bids, next_cursor_val, elapsed = _fetch_page(minimal)
                    attempted_without_status = True
                try:
                    if os.environ.get("FLOW_STATUS_DEBUG") and page_count == 1:
                        logging.getLogger("flow.status.provider").info(
                            f"mithril.task_query.page: status={status_group} bids={len(bids)} cursor={bool(next_cursor_val)}"
                        )
                except Exception:
                    pass
                api_time += elapsed

                if not bids:
                    break

                start_build = time.time()
                for bid in bids:
                    task_id = bid.get("fid", "")
                    if task_id and task_id not in seen_task_ids:
                        seen_task_ids.add(task_id)
                        task = self._task_service.build_task(bid, fetch_instance_details=False)
                        unique_tasks.append(task)
                build_time += time.time() - start_build

                next_cursor = next_cursor_val
                if next_cursor and next_cursor == last_cursor:
                    break
                last_cursor = next_cursor
                if not next_cursor:
                    break

        # Newest-first sort to ensure order if API misorders
        unique_tasks.sort(key=lambda t: t.created_at, reverse=True)

        # Defensive filtering: if a status filter was requested, ensure the
        # returned tasks actually match it even if the upstream API returns
        # mixed results. This keeps CLI expectations consistent (e.g.,
        # "active" views only show running/pending).
        if requested_statuses:
            # Defensive: ensure returned tasks match the requested filter even
            # if the upstream API returns mixed results. Since the API exposes
            # bid lifecycle states (Open/Allocated/Terminated/Paused/Preempting)
            # and our TaskStatus is different, map TaskStatus -> bid filter bucket.
            try:
                allowed = set(requested_statuses)

                def _to_bid_bucket(ts: TaskStatus | None) -> str | None:
                    if ts is None:
                        return None
                    if ts == TaskStatus.PENDING:
                        return "Open"
                    if ts == TaskStatus.RUNNING:
                        return "Allocated"
                    if ts == TaskStatus.PREEMPTING:
                        return "Preempting"
                    if ts == TaskStatus.PAUSED:
                        return "Paused"
                    # Terminal buckets
                    if ts in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                        return "Terminated"
                    return None

                unique_tasks = [
                    t for t in unique_tasks if _to_bid_bucket(getattr(t, "status", None)) in allowed
                ]
            except Exception:
                # If anything goes wrong, fall back to unfiltered list
                pass

        # Log debug timing for observability
        logger.info(
            "task_query.list_tasks: pages=%s api_time=%.3fs build_time=%.3fs tasks=%s",
            page_count,
            api_time,
            build_time,
            len(unique_tasks),
        )

        return unique_tasks[:limit]

    def list_active_tasks(self, limit: int = 100) -> list[Task]:
        return self.list_tasks(status=TaskStatus.RUNNING, limit=limit)

    def get_task(self, task_id: str) -> Task | None:
        """Get a single task by ID by paging over bids.

        Returns None if not found.
        """
        project_id = self._get_project_id()

        def _page(next_cursor: str | None = None):
            params: dict[str, Any] = {
                "project": project_id,
                "limit": 100,
                "sort_by": "created_at",
                "sort_dir": "desc",
            }
            if next_cursor:
                params["next_cursor"] = next_cursor
            return self._api.list_bids(params)

        bid = None
        next_cursor: str | None = None
        for _ in range(3):
            response = _page(next_cursor)
            if isinstance(response, list):
                bids = response
                next_cursor = None
            else:
                bids = response.get("data", [])
                next_cursor = response.get("next_cursor")
            bid = next((b for b in bids if (b.get("fid") or b.get("id")) == task_id), None)
            if bid or not next_cursor:
                break

        if not bid:
            return None

        # Single-task fetch can afford enrichment to resolve SSH and owner info accurately
        return self._task_service.build_task(bid, fetch_instance_details=True)

    def get_task_status(self, task_id: str) -> TaskStatus | None:
        """Get the current status of a task by scanning recent bids.

        Returns None if not found.
        """
        project_id = self._get_project_id()

        params: dict[str, Any] = {
            "project": project_id,
            "limit": 100,
            "sort_by": "created_at",
            "sort_dir": "desc",
        }

        response = self._api.list_bids(params)
        next_cursor = None
        pages_checked = 0
        bid = None
        while pages_checked < 3:
            pages_checked += 1
            if isinstance(response, list):
                bids = response
                next_cursor = None
            else:
                if response is None:
                    bids = []
                    next_cursor = None
                else:
                    bids = response.get("data", [])
                    next_cursor = response.get("next_cursor")

            bid = next((b for b in bids if (b.get("fid") or b.get("id")) == task_id), None)
            if bid or not next_cursor:
                break

            response = self._api.list_bids({**params, "next_cursor": next_cursor})

        if not bid:
            return None

        mithril_status = bid.get("status", "Pending")
        return self._task_service.map_mithril_status_to_enum(mithril_status)

    def get_bid_dict(self, task_id: str) -> dict | None:
        """Return the raw bid dict for a given task id or None if not found.

        This centralizes the pagination and search logic so provider code
        does not duplicate try/except scaffolding.
        """
        project_id = self._get_project_id()

        def _page(next_cursor: str | None = None):
            params: dict[str, Any] = {
                "project": project_id,
                "limit": 100,
                "sort_by": "created_at",
                "sort_dir": "desc",
            }
            if next_cursor:
                params["next_cursor"] = next_cursor
            return self._api.list_bids(params)

        next_cursor = None
        for _ in range(3):
            response = _page(next_cursor)
            if isinstance(response, list):
                bids = response
                next_cursor = None
            else:
                bids = response.get("data", [])
                next_cursor = response.get("next_cursor")
            bid = next((b for b in bids if (b.get("fid") or b.get("id")) == task_id), None)
            if bid:
                return bid
            if not next_cursor:
                break

        return None
