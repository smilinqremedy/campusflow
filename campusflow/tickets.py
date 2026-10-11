"""Ticket creation, validation, and priority calculation engine for CampusFlow.

Authored by Engineer A (Oche Gabriel Adanu).
"""

from typing import Any, Optional

ALLOWED_CATEGORIES = {"Network", "Hardware", "Software", "Other"}
ALLOWED_URGENCIES = {"low", "medium", "high"}


def validate_ticket_inputs(
    title: str,
    category: str,
    urgency: str,
    affected_users: Any
) -> tuple[str, str, str, int]:
    """Validate and normalize ticket input values.

    Args:
        title: Title of the problem (must be non-empty string).
        category: Category name (Network, Hardware, Software, Other).
        urgency: Urgency level (low, medium, high).
        affected_users: Number of affected campus users (strictly positive integer).

    Returns:
        tuple containing normalized (title, category, urgency, affected_users).

    Raises:
        ValueError: If any input fails validation criteria.
        TypeError: If inputs are of invalid types.
    """
    # 1. Title validation
    if not isinstance(title, str):
        raise TypeError("Ticket title must be a string.")
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Ticket title must not be blank.")

    # 2. Category validation & normalization
    if not isinstance(category, str):
        raise TypeError("Ticket category must be a string.")
    clean_category = category.strip()
    normalized_category = None
    for allowed in ALLOWED_CATEGORIES:
        if clean_category.lower() == allowed.lower():
            normalized_category = allowed
            break
    if normalized_category is None:
        raise ValueError(
            f"Invalid category '{category}'. Allowed categories: {', '.join(sorted(ALLOWED_CATEGORIES))}."
        )

    # 3. Urgency validation & normalization
    if not isinstance(urgency, str):
        raise TypeError("Ticket urgency must be a string.")
    clean_urgency = urgency.strip().lower()
    if clean_urgency not in ALLOWED_URGENCIES:
        raise ValueError(
            f"Invalid urgency '{urgency}'. Allowed urgency levels: {', '.join(sorted(ALLOWED_URGENCIES))}."
        )

    # 4. Affected users validation
    # Guard against booleans since bool is a subclass of int in Python
    if isinstance(affected_users, bool) or not isinstance(affected_users, int):
        raise ValueError("Affected users must be a positive integer.")
    if affected_users <= 0:
        raise ValueError("Affected users must be greater than zero.")

    return clean_title, normalized_category, clean_urgency, affected_users


def calculate_priority(urgency: str, affected_users: int) -> str:
    """Calculate ticket priority based on strict business logic rules.

    Rules are evaluated in exact priority order (first match wins):
      RULE 1: high urgency AND 10 or more affected users  -> critical
      RULE 2: high urgency OR 10 or more affected users   -> high
      RULE 3: medium urgency OR 3 or more affected users  -> medium
      RULE 4: all remaining valid tickets                 -> low

    Args:
        urgency: Normalized urgency string ('low', 'medium', 'high').
        affected_users: Positive integer number of affected users.

    Returns:
        Priority level ('critical', 'high', 'medium', 'low').
    """
    norm_urgency = urgency.lower()

    # RULE 1: high urgency AND 10 or more affected users -> critical
    if norm_urgency == "high" and affected_users >= 10:
        return "critical"

    # RULE 2: high urgency OR 10 or more affected users -> high
    if norm_urgency == "high" or affected_users >= 10:
        return "high"

    # RULE 3: medium urgency OR 3 or more affected users -> medium
    if norm_urgency == "medium" or affected_users >= 3:
        return "medium"

    # RULE 4: all remaining valid tickets -> low
    return "low"


def generate_ticket_id(existing_tickets: list[dict]) -> str:
    """Generate next sequential ticket ID (e.g. T001, T002, ...).

    Safely parses highest numerical ID suffix to prevent collisions even if
    tickets have gaps or were reloaded from storage.

    Args:
        existing_tickets: List of existing ticket dictionaries.

    Returns:
        New unique ticket ID string.
    """
    max_num = 0
    if existing_tickets:
        for t in existing_tickets:
            tid = t.get("id", "")
            if isinstance(tid, str) and tid.startswith("T") and tid[1:].isdigit():
                max_num = max(max_num, int(tid[1:]))

    next_num = max_num + 1
    return f"T{next_num:03d}"


def create_ticket(
    title: str,
    category: str,
    urgency: str,
    affected_users: Any,
    existing_tickets: Optional[list[dict]] = None
) -> dict:
    """Validate inputs, calculate priority, assign ID, and create ticket dictionary.

    Args:
        title: Short description of the issue.
        category: Department category.
        urgency: Level of urgency.
        affected_users: Count of impacted users.
        existing_tickets: Optional list of existing tickets to append to and verify IDs.

    Returns:
        Newly created ticket dictionary.
    """
    clean_title, norm_category, norm_urgency, valid_users = validate_ticket_inputs(
        title=title,
        category=category,
        urgency=urgency,
        affected_users=affected_users
    )

    tickets_list = existing_tickets if existing_tickets is not None else []
    ticket_id = generate_ticket_id(tickets_list)
    priority = calculate_priority(norm_urgency, valid_users)

    ticket = {
        "id": ticket_id,
        "title": clean_title,
        "category": norm_category,
        "urgency": norm_urgency,
        "affected_users": valid_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }

    if existing_tickets is not None:
        existing_tickets.append(ticket)

    return ticket


def get_ticket_by_id(tickets: list[dict], ticket_id: str) -> Optional[dict]:
    """Retrieve ticket dictionary by its unique ID.

    Args:
        tickets: List of ticket dictionaries.
        ticket_id: Ticket ID to search for (case-insensitive comparison).

    Returns:
        Ticket dict if found, else None.
    """
    target = ticket_id.strip().upper()
    for t in tickets:
        if t.get("id", "").upper() == target:
            return t
    return None


def is_valid_ticket_id(ticket_id: str) -> bool:
    """Check if a string is a valid ticket ID format (e.g. 'T001', 'T100').

    Args:
        ticket_id: String to validate.

    Returns:
        True if formatted as 'T' followed by 3 or more digits, else False.
    """
    if not isinstance(ticket_id, str):
        return False
    clean = ticket_id.strip().upper()
    return clean.startswith("T") and clean[1:].isdigit() and len(clean[1:]) >= 3


def format_ticket_summary(ticket: dict) -> str:
    """Format a ticket dictionary into a concise one-line summary string.

    Args:
        ticket: Ticket dictionary.

    Returns:
        Single-line formatted summary.
    """
    tid = ticket.get("id", "N/A")
    title = ticket.get("title", "Untitled")
    category = ticket.get("category", "General")
    priority = ticket.get("priority", "N/A").upper()
    status = ticket.get("status", "open")
    assigned = ticket.get("assigned_to") or "Unassigned"
    return f"[{tid}] {title} | {category} | {priority} | {status} | Assigned: {assigned}"



def format_ticket_details(ticket: dict) -> str:
    """Format full ticket details into a human-readable multi-line block.

    Args:
        ticket: Ticket dictionary.

    Returns:
        Multi-line formatted string.
    """
    lines = [
        "=" * 50,
        f"Ticket ID:       {ticket.get('id', 'N/A')}",
        f"Title:           {ticket.get('title', 'N/A')}",
        f"Category:        {ticket.get('category', 'N/A')}",
        f"Urgency:         {ticket.get('urgency', 'N/A')}",
        f"Affected Users:  {ticket.get('affected_users', 'N/A')}",
        f"Priority:        {str(ticket.get('priority', 'N/A')).upper()}",
        f"Status:          {ticket.get('status', 'N/A')}",
        f"Assigned To:     {ticket.get('assigned_to') or 'Unassigned'}",
        "=" * 50,
    ]
    return "\n".join(lines)

