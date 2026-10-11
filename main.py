"""CampusFlow — Command-Line Helpdesk Ticket Management System.

Integrates ticket creation, workflow lifecycle, work queues, reporting, and persistence.
"""

from __future__ import annotations

import sys
from pathlib import Path

from campusflow.reports import build_report, work_queue
from campusflow.storage import (
    DEFAULT_STORAGE_PATH,
    StorageError,
    load_tickets,
    save_tickets,
)
from campusflow.tickets import (
    ALLOWED_CATEGORIES,
    ALLOWED_URGENCIES,
    create_ticket,
    format_ticket_details,
    format_ticket_summary,
    get_ticket_by_id,
)
from campusflow.workflow import assign_ticket, change_status


def print_header(title: str) -> None:
    """Print section banner."""
    print("\n" + "=" * 60)
    print(f"  {title.upper()}")
    print("=" * 60)


def print_menu() -> None:
    """Display interactive CLI options."""
    print("\n------------------------------------------------------------")
    print("  CAMPUSFLOW HELPDESK SYSTEM")
    print("------------------------------------------------------------")
    print("  [1] Create New Ticket")
    print("  [2] List All Tickets")
    print("  [3] View Ticket Details")
    print("  [4] Assign Ticket to Staff")
    print("  [5] Update Ticket Status")
    print("  [6] View Work Queue (Priority Order)")
    print("  [7] Generate Summary Report")
    print("  [8] Save and Exit")
    print("------------------------------------------------------------")


def handle_create_ticket(tickets: list[dict], storage_path: Path) -> None:
    """Collect inputs and create a new ticket."""
    print_header("F1 — Create Ticket")
    title = input("Enter problem title: ").strip()
    if not title:
        print("[ERROR] Ticket title must not be blank.")
        return

    print(f"Allowed categories: {', '.join(sorted(ALLOWED_CATEGORIES))}")
    category = input("Enter category: ").strip()

    print(f"Allowed urgency levels: {', '.join(sorted(ALLOWED_URGENCIES))}")
    urgency = input("Enter urgency: ").strip()

    raw_users = input("Enter number of affected users: ").strip()
    try:
        # Prevent float strings like '3.5'
        if "." in raw_users:
            print("[ERROR] Affected users must be an integer, not a decimal.")
            return
        affected_users = int(raw_users)
    except ValueError:
        print("[ERROR] Affected users must be a valid integer.")
        return

    try:
        new_ticket = create_ticket(
            title=title,
            category=category,
            urgency=urgency,
            affected_users=affected_users,
            existing_tickets=tickets,
        )
        save_tickets(tickets, storage_path)
        print(f"\n[SUCCESS] Ticket {new_ticket['id']} created successfully!")
        print(f"Priority calculated: {new_ticket['priority'].upper()}")
        print(f"Initial status:      {new_ticket['status']}")
    except ValueError as err:
        print(f"[ERROR] Validation failed: {err}")


def handle_list_tickets(tickets: list[dict]) -> None:
    """List all tickets in concise overview."""
    print_header("F2 — List All Tickets")
    if not tickets:
        print("No tickets found in the system.")
        return

    print(f"Total tickets: {len(tickets)}\n")
    for t in tickets:
        print(format_ticket_summary(t))


def handle_view_ticket(tickets: list[dict]) -> None:
    """View full details for a chosen ticket."""
    print_header("F2 — View Ticket Details")
    tid = input("Enter Ticket ID (e.g. T001): ").strip()
    ticket = get_ticket_by_id(tickets, tid)
    if not ticket:
        print(f"[ERROR] No ticket found with ID '{tid.upper()}'.")
        return

    print(format_ticket_details(ticket))


def handle_assign_ticket(tickets: list[dict], storage_path: Path) -> None:
    """Assign ticket to staff member."""
    print_header("F3 — Assign Ticket")
    tid = input("Enter Ticket ID to assign: ").strip()
    staff_name = input("Enter staff member name: ").strip()

    try:
        updated = assign_ticket(tickets, tid, staff_name)
        save_tickets(tickets, storage_path)
        print(f"\n[SUCCESS] Ticket {updated['id']} assigned to '{updated['assigned_to']}'.")
    except ValueError as err:
        print(f"[ERROR] Assignment failed: {err}")


def handle_update_status(tickets: list[dict], storage_path: Path) -> None:
    """Update ticket workflow status."""
    print_header("F4 — Update Ticket Status")
    tid = input("Enter Ticket ID to update: ").strip()
    ticket = get_ticket_by_id(tickets, tid)
    if not ticket:
        print(f"[ERROR] No ticket found with ID '{tid.upper()}'.")
        return

    print(f"Current status: {ticket['status']}")
    print(f"Assigned to:    {ticket.get('assigned_to') or 'Unassigned'}")
    print("Allowed targets: open, in_progress, resolved")
    new_status = input("Enter new status: ").strip().lower()

    try:
        updated = change_status(tickets, tid, new_status)
        save_tickets(tickets, storage_path)
        print(f"\n[SUCCESS] Ticket {updated['id']} status updated to '{updated['status']}'.")
    except ValueError as err:
        print(f"[ERROR] Status transition failed: {err}")


def handle_work_queue(tickets: list[dict]) -> None:
    """Display pending work queue ordered by priority and numeric ID."""
    print_header("F5 — Work Queue (Pending Tickets)")
    queue = work_queue(tickets)
    if not queue:
        print("Work queue is empty. No unresolved tickets!")
        return

    print(f"Unresolved tickets in queue: {len(queue)}\n")
    for rank, t in enumerate(queue, start=1):
        assigned = t.get("assigned_to") or "Unassigned"
        print(f"{rank:2d}. [{t['id']}] {t['priority'].upper():<8} | {t['status']:<11} | Users: {t['affected_users']:<3} | {t['title']:<25} | Staff: {assigned}")


def handle_reports(tickets: list[dict]) -> None:
    """Display aggregate system reports."""
    print_header("F6 — System Reports & Statistics")
    report = build_report(tickets)

    print(f"Total Tickets Recorded: {report['total']}\n")

    print("Breakdown by Status:")
    for status, count in report["by_status"].items():
        print(f"  • {status:<15}: {count}")

    print("\nBreakdown by Priority:")
    for priority, count in report["by_priority"].items():
        print(f"  • {priority.upper():<15}: {count}")


def main() -> None:
    """Application entry point."""
    storage_path = DEFAULT_STORAGE_PATH

    print("\nStarting CampusFlow Helpdesk System...")
    try:
        tickets = load_tickets(storage_path)
        print(f"[INFO] Loaded {len(tickets)} existing ticket(s) from '{storage_path}'.")
    except StorageError as err:
        print(f"\n[CRITICAL ERROR] {err}")
        print("To protect your data, the application will exit without modifying the file.")
        print("Please resolve the JSON syntax error in 'data/tickets.json' or delete it to start fresh.")
        sys.exit(1)

    while True:
        try:
            print_menu()
            choice = input("Select an option (1-8): ").strip()

            if choice == "1":
                handle_create_ticket(tickets, storage_path)
            elif choice == "2":
                handle_list_tickets(tickets)
            elif choice == "3":
                handle_view_ticket(tickets)
            elif choice == "4":
                handle_assign_ticket(tickets, storage_path)
            elif choice == "5":
                handle_update_status(tickets, storage_path)
            elif choice == "6":
                handle_work_queue(tickets)
            elif choice == "7":
                handle_reports(tickets)
            elif choice == "8":
                save_tickets(tickets, storage_path)
                print("\n[INFO] All changes saved successfully. Thank you for using CampusFlow!")
                break
            else:
                print("[ERROR] Invalid choice. Please select an option between 1 and 8.")
        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupt received. Saving tickets before exit...")
            save_tickets(tickets, storage_path)
            print("[INFO] Saved. Goodbye!")
            break
        except Exception as err:
            print(f"[UNEXPECTED ERROR] {err}")


if __name__ == "__main__":
    main()
