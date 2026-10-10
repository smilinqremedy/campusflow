"""Ticket assignment and lifecycle rules."""

from __future__ import annotations

from typing import Any

from .tickets import get_ticket_by_id


def _find_ticket(
    tickets: list[dict[str, Any]],
    ticket_id: str,
) -> dict[str, Any]:
    """Find a ticket or raise ValueError if it does not exist."""

    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Ticket ID must not be blank.")

    ticket = get_ticket_by_id(tickets, ticket_id)

    if ticket is None:
        raise ValueError(
            f"No ticket found with ID {ticket_id.strip().upper()}."
        )

    return ticket


def assign_ticket(
    tickets: list[dict[str, Any]],
    ticket_id: str,
    staff_name: str,
) -> dict[str, Any]:
    """Assign a ticket to a staff member."""

    ticket = _find_ticket(tickets, ticket_id)

    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff member name must not be blank.")

    if ticket["status"] == "resolved":
        raise ValueError(
            "A resolved ticket must be reopened before it can be modified."
        )

    ticket["assigned_to"] = staff_name.strip()

    return ticket


def change_status(
    tickets: list[dict[str, Any]],
    ticket_id: str,
    new_status: str,
) -> dict[str, Any]:
    """Change a ticket's status according to the allowed workflow."""

    ticket = _find_ticket(tickets, ticket_id)

    if not isinstance(new_status, str):
        raise ValueError("Status must be open, in_progress, or resolved.")

    target = new_status.strip().lower()

    if target not in {"open", "in_progress", "resolved"}:
        raise ValueError("Status must be open, in_progress, or resolved.")

    current = ticket["status"]

    # A resolved ticket can only be reopened to open.
    if current == "resolved":
        if target != "open":
            raise ValueError(
                "A resolved ticket must be explicitly reopened to open first."
            )

        ticket["status"] = "open"
        return ticket

    # An open ticket must be assigned before work can begin.
    if current == "open" and target == "in_progress":
        if not ticket.get("assigned_to"):
            raise ValueError(
                "Assign the ticket to a staff member before starting work."
            )

        ticket["status"] = "in_progress"
        return ticket

    # Work in progress can be marked resolved.
    if current == "in_progress" and target == "resolved":
        ticket["status"] = "resolved"
        return ticket

    if target == current:
        raise ValueError(f"Ticket is already {current}.")

    raise ValueError(f"Invalid status transition: {current} -> {target}.")
