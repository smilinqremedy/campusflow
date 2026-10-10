# Design Decisions & Function Contracts

**Project:** CampusFlow  
**Team:** Campusflow-Adanu&Fredrick  
**Authors:** Oche Gabriel Adanu (Engineer A) & Ocheche Fredrick (Engineer B)  

This document details the shared architectural agreements, data models, error handling strategies, and module interfaces agreed upon prior to coding.

---

## 1. Data Model Specification

Each ticket is represented as a standard Python dictionary:

```python
{
    "id": "T001",                 # string: unique sequential ID (T001, T002, ...)
    "title": "Campus Wi-Fi down", # string: non-empty, stripped of leading/trailing spaces
    "category": "Network",        # string: one of {"Network", "Hardware", "Software", "Other"}
    "urgency": "high",            # string: one of {"low", "medium", "high"} (normalized to lowercase)
    "affected_users": 15,         # int: strictly positive integer (> 0)
    "priority": "critical",       # string: one of {"critical", "high", "medium", "low"}
    "status": "open",             # string: one of {"open", "in_progress", "resolved"}
    "assigned_to": None           # string or None: non-empty staff name when assigned
}
```

### Allowed Categories and Normalization
- Allowed categories: `"Network"`, `"Hardware"`, `"Software"`, `"Other"`.
- Normalization: Input matching is case-insensitive, normalized to title-case (e.g., `"network"` -> `"Network"`). Any other value raises a `ValueError`.

### Urgency Levels
- Allowed urgencies: `"low"`, `"medium"`, `"high"`.
- Normalization: Normalized to lowercase.

### Affected Users
- Must be a strictly positive integer (`> 0`). Rejects `0`, negative numbers, floating-point numbers, and non-numeric strings.

---

## 2. Priority Engine Specification (Strict Evaluation Order)

Priority is calculated deterministically through ordinary Python business logic. Rules are evaluated in the exact order specified; the first matching rule dictates the ticket's priority:

1. **Rule 1 — Critical**: `urgency == "high" and affected_users >= 10`
2. **Rule 2 — High**: `urgency == "high" or affected_users >= 10`
3. **Rule 3 — Medium**: `urgency == "medium" or affected_users >= 3`
4. **Rule 4 — Low**: All other valid combinations (e.g. `urgency == "low"` with `1` or `2` affected users).

---

## 3. Core Architectural Questions & Agreements

### Q1: Where is the ticket collection stored and how is it passed between functions?
- **Decision**: In memory, the ticket collection is maintained as a Python `list` of ticket dictionaries.
- **Passing Mechanism**: Functions accept the ticket list as an explicit argument (e.g., `tickets: list[dict]`). This keeps functions pure, predictable, and simple to unit-test without relying on global state.

### Q2: How does a function signal invalid input, and how does the CLI display it?
- **Decision**: Business logic functions raise Python standard `ValueError` (or descriptive domain-specific exceptions) with clear, human-readable error messages when constraints are violated.
- **CLI Handling**: The CLI layer (`main.py`) catches exceptions inside `try ... except ValueError as err:` blocks and displays a formatted error prompt to the user (e.g. `[ERROR] Invalid affected users: must be a positive integer`), allowing the user to correct their input without the application crashing.

### Q3: What is the expected return value when a ticket is created, assigned, or updated?
- **`create_ticket(...)`**: Returns the newly created ticket dictionary. It also appends the ticket to the passed ticket collection.
- **`assign_ticket(tickets, ticket_id, staff_name)`**: Returns the modified ticket dictionary. Raises `ValueError` or `KeyError` if `ticket_id` is not found or `staff_name` is blank.
- **`update_status(tickets, ticket_id, new_status)`**: Returns the modified ticket dictionary. Raises `ValueError` if the transition is illegal (e.g., moving unassigned ticket to `in_progress`, or mutating a `resolved` ticket without reopening).

### Q4: Which module owns loading/saving JSON and how do other modules call it?
- **Decision**: The `campusflow.storage` module owns all serialization and file I/O operations.
- **Signatures**:
  - `load_tickets(filepath: str) -> list[dict]`:
    - Returns `[]` if the file does not exist (fresh start).
    - Raises `ValueError` / `json.JSONDecodeError` with clear error details if the JSON file is malformed.
  - `save_tickets(filepath: str, tickets: list[dict]) -> None`:
    - Safely writes tickets to the target JSON file with indentation (`indent=2`), ensuring directories exist.
- **ID Preservation**: Ticket ID generation determines the next sequential ID by parsing all existing IDs in the collection (`max_id + 1`), ensuring no ID collisions occur upon restarting or reloading.

### Q5: How can we test business logic without interactive CLI prompts?
- **Decision**: Strict separation of concerns.
  - Business logic resides entirely in `campusflow/tickets.py`, `campusflow/workflow.py`, `campusflow/storage.py`, and `campusflow/reports.py`. None of these modules invoke `input()` or `print()`.
  - The CLI menu in `main.py` handles user prompts and console formatting only, delegating all operations to the core modules.
  - Test suites in `tests/` invoke the core functions directly with mock data, asserting results cleanly with zero interactive input.

---

## 4. Module Responsibilities & Ownership

```
campusflow/
├── tickets.py     (Engineer A: Validation, ID generation, Priority engine, Creation)
├── workflow.py    (Engineer B: Assignment, Lifecycle state transitions, Reopening)
├── reports.py     (Engineer B: Work queue sorting, Summary statistics)
├── storage.py     (Shared: Safe JSON load/save, error reporting)
└── main.py        (Shared: Text-based interactive CLI menu)
```
