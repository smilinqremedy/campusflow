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

### Interaction #1 — Multi-Criteria Queue Sorting and Tie-Breaking in Python
- **Problem**: I needed to sort open tickets first by custom priority ranking (`critical` > `high` > `medium` > `low`), and then break ties between tickets of the same priority by their numeric ticket ID (`T001` before `T002`).
- **My initial understanding**: I considered running multiple sorting passes with `list.sort()`.
- **Prompt to AI**: "How does Python's `sorted()` function handle multiple sort criteria with custom ranking and numerical tie-breaking?"
- **Useful AI guidance**: The AI explained that returning a tuple from the key function (`key=lambda x: (criterion_1, criterion_2)`) evaluates criteria in lexicographical order: Python sorts by the first tuple element, and only if there is a tie does it compare the second element.
- **My independent experiment/test**:
  ```python
  tickets = [
      {"id": "T002", "priority": "high"},
      {"id": "T001", "priority": "high"},
      {"id": "T003", "priority": "critical"},
  ]
  _PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
  sorted_tickets = sorted(
      tickets,
      key=lambda t: (_PRIORITY_RANK[t["priority"]], int(t["id"][1:]))
  )
  print([t["id"] for t in sorted_tickets])  # Output: ['T003', 'T001', 'T002']
  ```
- **Verification source or result**: Verified that `T003` (critical) sorts first, followed by `T001` (high, ID 1), then `T002` (high, ID 2).
- **Decision**: Implemented `sort_key(ticket: dict) -> tuple[int, int, str]` in `campusflow.reports.work_queue`.
- **Related file/commit**: `campusflow/reports.py` (`work_queue`), `tests/test_workflow.py` (`test_queue_priority_then_numeric_id`).
- **What I can now explain without AI**: Tuple comparison in Python natively solves multi-level sorting. By mapping categorical strings to numeric ranks in the first tuple position and ticket IDs in the second, ties are broken automatically without secondary passes.

---

### Interaction #2 — Workflow Lifecycle State Guards & Reopening Rules
- **Problem**: Enforcing that an unassigned ticket cannot move to `in_progress`, and that a `resolved` ticket cannot be mutated without an explicit reopen operation.
- **My initial understanding**: I initially considered a simple dictionary mapping allowed `(current_status, new_status)` pairs.
- **Prompt to AI**: "What is the cleanest way to validate state machine transitions with business guards in Python?"
- **Useful AI guidance**: The AI showed that while a transition table works for simple state changes, guard conditions that depend on ticket attributes (like verifying `ticket.get("assigned_to")` is non-empty before entering `in_progress`) require explicit guard checks before committing the status change.
- **My independent experiment/test**:
  Tested attempting to progress an unassigned ticket:
  ```python
  ticket = {"id": "T001", "status": "open", "assigned_to": None}
  # Attempt invalid transition
  if not ticket.get("assigned_to"):
      raise ValueError("Assign the ticket to a staff member before starting work.")
  ```
- **Verification source or result**: Automated tests in `tests/test_workflow.py` (`test_unassigned_ticket_cannot_start`) verified that `ValueError` is raised and status remains `"open"`.
- **Decision**: Implemented procedural guard validation in `campusflow.workflow.change_status`.
- **Related file/commit**: `campusflow/workflow.py` (`change_status`), `tests/test_workflow.py`.
- **What I can now explain without AI**: State transitions with attribute preconditions (guards) are best validated explicitly before mutating object state, ensuring invalid transitions fail fast without leaving tickets in an inconsistent or partially updated state.

---

### Interaction #3 — Safe Dictionary Aggregation and Zero-Count Handling [CRITICAL EVALUATION / REJECTED AI SUGGESTION]
- **Problem**: Generating aggregate summary reports by status and priority, including when the ticket collection is empty (0 tickets).
- **My initial understanding**: I needed total tickets and counts broken down by status and priority.
- **Prompt to AI**: "Write a Python function to aggregate ticket counts by status and priority using `collections.Counter`."
- **Useful AI guidance**: The AI suggested using `collections.Counter(t['status'] for t in tickets)` and `collections.Counter(t['priority'] for t in tickets)`.
- **My independent experiment/test**:
  When tested against an empty ticket list (`tickets = []`) or a list with only 1 category present:
  ```python
  from collections import Counter
  c = Counter([t.get("status") for t in []])
  print(dict(c))  # Output: {}
  ```
  The naive suggestion returned an empty dictionary `{}`. In the CLI and reporting requirements, missing statuses or priorities (such as `0` resolved tickets or `0` critical tickets) would be completely omitted from the report output instead of displaying `open: 0`, `in_progress: 0`, `resolved: 0`.
- **Verification source or result**: Verified that requirement F6 requires displaying counts even when a status has 0 tickets.
- **Decision**: **IMPROVED/REJECTED the Counter suggestion**. Instead of returning a sparse dictionary from `Counter`, I pre-initialized all allowed statuses and priorities with default zero counts:
  ```python
  statuses = {"open": 0, "in_progress": 0, "resolved": 0}
  priorities = {priority: 0 for priority in PRIORITIES}
  ```
- **Related file/commit**: `campusflow/reports.py` (`build_report`), `tests/test_workflow.py` (`test_empty_report`).
- **What I can now explain without AI**: Using sparse counters (`collections.Counter`) misses zero-count categories when items are absent. Pre-initializing known categorical keys guarantees consistent reporting schema even for edge cases like empty collections.

