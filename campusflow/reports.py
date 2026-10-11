"""Work queue ordering and aggregate reports."""
from __future__ import annotations

from typing import Any
PRIORITIES = ("critical", "high", "medium", "low")

_PRIORITY_RANK = {priority: index for index, priority in enumerate(PRIORITIES)}


def work_queue(tickets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return unresolved tickets ordered by priority, then numeric ticket ID."""
    unresolved = [
        ticket
        for ticket in tickets
        if ticket.get("status") in {"open", "in_progress"}
    ]

    def sort_key(ticket: dict[str, Any]) -> tuple[int, int, str]:
        priority_rank = _PRIORITY_RANK.get(
            ticket.get("priority"),
            len(PRIORITIES),
        )
        ticket_id = ticket.get("id", "")
        suffix = (
            ticket_id[1:]
            if isinstance(ticket_id, str) and ticket_id.startswith("T")
            else ""
        )
        numeric_id = int(suffix) if suffix.isdigit() else 10**12

        return priority_rank, numeric_id, str(ticket_id)

    return sorted(unresolved, key=sort_key)



def build_report(tickets: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = {"open": 0, "in_progress": 0, "resolved": 0}
    priorities = {priority: 0 for priority in PRIORITIES}
    for ticket in tickets:
        status = ticket.get("status")
        priority = ticket.get("priority")
        if status in statuses:
            statuses[status] += 1
        if priority in priorities:
            priorities[priority] += 1
    return {"total": len(tickets), "by_status": statuses, "by_priority": priorities}
