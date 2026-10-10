# AI-Native Engineering Learning Log

**Team:** Campusflow-Adanu&Fredrick  
**Sprint:** AI-Native Engineering Sprint — CampusFlow  

---

## Fellow: Oche Gabriel Adanu (Engineer A)

### Interaction #1 — Python Input Validation: Integers vs Booleans and Strict Boundaries
- **Problem**: I needed to ensure `affected_users` is strictly a positive integer (not zero, negative, float, or boolean).
- **My initial understanding**: I initially thought using `isinstance(val, int)` and `val > 0` was sufficient to validate integers.
- **Prompt to AI**: "In Python, how does `isinstance(x, int)` handle boolean values and strings, and what is the safest way to validate that an input is strictly a positive integer?"
- **Useful AI guidance**: The AI explained that in Python, `bool` is actually a subclass of `int` (`issubclass(bool, int) is True`). Therefore, `isinstance(True, int)` evaluates to `True`, which would inadvertently treat `True` as integer `1`. To strictly enforce positive integers, we must explicitly verify `isinstance(val, int) and not isinstance(val, bool) and val > 0`.
- **My independent experiment/test**:
  ```python
  val = True
  isinstance(val, int)  # Output: True
  # Strict check
  is_valid = isinstance(val, int) and not isinstance(val, bool) and val > 0  # Output: False
  ```
- **Verification source or result**: Ran experiment in Python 3.12 interactive shell. Tested `[15, 0, -5, 3.5, "15", True, False]`. Only `15` passed validation.
- **Decision**: Accepted and applied in `campusflow/tickets.py` input validation functions.
- **Related file/commit**: `campusflow/tickets.py`, `tests/test_tickets.py` (`test_validate_affected_users_rejects_zero_and_negative`).
- **What I can now explain without AI**: In Python's object model, `bool` inherits from `int`. Any strict numerical validation must exclude `bool` to prevent Boolean flags from being parsed as integer `1` or `0`.

---

### Interaction #2 — Rule Precedence and Boundary Conditions in Priority Engines
- **Problem**: I needed to implement the four priority rules in strict order without logic overlap bugs.
- **My initial understanding**: I considered combining rules with multiple boolean operators or evaluating urgency and user counts independently.
- **Prompt to AI**: "Show me how checking overlapping conditions in sequence using `if ... elif ... else` prevents subtle priority bugs in Python business logic."
- **Useful AI guidance**: The AI showed that because Rule 1 (`high` AND `>= 10` -> `critical`) is a subset of Rule 2 (`high` OR `>= 10` -> `high`), evaluating Rule 2 before Rule 1 would swallow all critical tickets and misclassify them as high. An ordered `if / elif / else` ladder guarantees that the most specific condition (Rule 1) intercepts matching cases first.
- **My independent experiment/test**:
  Tested boundary values:
  - `high` urgency with `12` users -> `critical`
  - `high` urgency with `2` users -> `high`
  - `low` urgency with `10` users -> `high` (Rule 2 boundary)
  - `low` urgency with `4` users -> `medium` (Rule 3 boundary)
  - `low` urgency with `1` user -> `low` (Rule 4 default)
- **Verification source or result**: Executed isolated test script confirming all guide scenarios match requirements.
- **Decision**: Implemented an explicit `if / elif / else` ladder in `campusflow.tickets.calculate_priority`.
- **Related file/commit**: `campusflow/tickets.py` (`calculate_priority`), `tests/test_tickets.py`.
- **What I can now explain without AI**: When rules share criteria (like `high` urgency in both Rule 1 and Rule 2), order of evaluation dictates precedence. By evaluating conjunctions (`AND`) before disjunctions (`OR`), we ensure higher-severity rules are triggered first.

---

### Interaction #3 — Unique ID Generation: Collision Risk with `len(tickets) + 1` [CRITICAL EVALUATION / REJECTED AI SUGGESTION]
- **Problem**: I needed to generate unique IDs (`T001`, `T002`, ...) that remain unique across restarts and after file reloads.
- **My initial understanding**: I wanted an automatic counter that builds IDs formatted as `T` followed by a three-digit integer.
- **Prompt to AI**: "Write a Python function to generate the next sequential ticket ID from a list of ticket dictionaries."
- **Useful AI guidance**: The AI suggested using `f"T{len(tickets) + 1:03d}"`.
- **My independent experiment/test**:
  I set up an experiment where `tickets = [{"id": "T001"}, {"id": "T003"}]` (simulating a list where tickets were filtered, deleted, or partially archived):
  ```python
  naive_id = f"T{len(tickets) + 1:03d}"  # Output: "T003" -> DUPLICATE COLLISION!
  ```
  The naive suggestion produced `T003`, which already existed in the collection, violating the uniqueness constraint.
- **Verification source or result**: Verified that `any(t["id"] == "T003" for t in tickets)` returned `True`.
- **Decision**: **REJECTED the AI suggestion**. Instead, I wrote a safe ID generator that extracts the highest numerical suffix from existing tickets and increments it:
  ```python
  def generate_ticket_id(existing_tickets: list[dict]) -> str:
      max_id = 0
      for t in existing_tickets:
          tid = t.get("id", "")
          if tid.startswith("T") and tid[1:].isdigit():
              max_id = max(max_id, int(tid[1:]))
      return f"T{max_id + 1:03d}"
  ```
- **Related file/commit**: `campusflow/tickets.py` (`generate_ticket_id`), `tests/test_tickets.py` (`test_generate_ticket_id_handles_gaps_without_collision`).
- **What I can now explain without AI**: Counting elements with `len()` is state-dependent and unsafe for sequential ID assignment when items can be removed, archived, or reloaded with gaps. Parsing the maximum existing key guarantees strictly increasing, non-colliding IDs.

---

## Fellow: Ocheche Fredrick (Engineer B)

*(To be recorded by Engineer B during Phase 3 & 4 development on branch `feat/2-workflow-and-reports`)*

### Interaction #1 — Ticket Assignment and Validation
- **Problem**: Restricting ticket status transitions so unassigned tickets cannot enter `in_progress`.
- *Status: In progress by Engineer B.*

### Interaction #2 — Priority Queue Sorting with Tie-breaking
- **Problem**: Sorting open tickets by custom priority order (`critical` > `high` > `medium` > `low`) and breaking ties by numeric ID.
- *Status: In progress by Engineer B.*

### Interaction #3 — Reopening Resolved Tickets and Lifecycle Rules
- **Problem**: Enforcing that resolved tickets cannot be edited without an explicit reopen operation.
- *Status: In progress by Engineer B.*
