# CampusFlow — Technical Support Helpdesk

**AI-Native Engineering Sprint Challenge**  
**Team:** Campusflow-Adanu&Fredrick  

CampusFlow is a robust, modular Python command-line ticket management system built for campus technical support staff at Learn2Earn. It records problems, validates input, calculates priority through deterministic business rules, tracks ticket assignment and lifecycle stages, orders work queues, generates operational reports, and persists state safely using JSON storage.

---

## 👥 Engineering Team & Responsibilities

| Fellow | Role | Primary Responsibilities | Feature Branch |
| :--- | :--- | :--- | :--- |
| **Oche Gabriel Adanu** ([@Aocheg](https://github.com/Aocheg)) | **Engineer A** | • F1: Ticket Creation & Input Validation<br>• F1.3: Priority Calculation Engine<br>• Unit tests in `tests/test_tickets.py`<br>• AI Learning Log entries (Engineer A)<br>• Pull Request review on Engineer B's work | `feat/1-ticket-creation` |
| **Ocheche Fredrick** ([@smilinqremedy](https://github.com/smilinqremedy)) | **Engineer B** | • F3: Ticket Assignment<br>• F4: Status Workflow (`open` → `in_progress` → `resolved`)<br>• F5: Priority Work Queue<br>• F6: Summary & Category Reporting<br>• Unit tests in `tests/test_workflow.py`<br>• AI Learning Log entries (Engineer B)<br>• Pull Request review on Engineer A's work | `feat/3-6-assignment-workflow-reports` |
| **Both Fellows** | **Collaboration** | • Architectural contract (`docs/design-decisions.md`)<br>• F7: JSON Persistence & reload safety (`campusflow/storage.py`)<br>• CLI interaction layer (`main.py`)<br>• Full regression test verification on `main` | `main` |

---

## 🚀 Setup & Installation

### Requirements
- **Python**: 3.10+ (Tested on Python 3.12)
- Standard Library only (`unittest`, `json`, `os`, `sys`, `pathlib`) — No third-party dependencies required.

### Clone the Repository
```bash
git clone https://github.com/smilinqremedy/campusflow.git
cd campusflow
```

---

## 💻 Running the Application

Launch the interactive CLI menu:
```bash
python3 main.py
```

### Available Menu Options
1. **Create Ticket** — Submit title, category, urgency, and affected users.
2. **List All Tickets** — Display a tabular overview of all recorded tickets.
3. **View Ticket Details** — View the complete record for a specific ticket ID.
4. **Assign Ticket** — Assign a ticket to a staff member.
5. **Update Status** — Progress ticket status (`open` → `in_progress` → `resolved`, or reopen).
6. **Show Work Queue** — View pending tickets sorted by priority level and ticket ID.
7. **View Reports** — Display summary statistics broken down by status and priority.
8. **Exit** — Save state and exit application.

---

## 🧪 Running Automated Tests

Run the full automated test suite (33 tests) using Python's standard `unittest` discovery:
```bash
python3 -m unittest discover -s tests -v
```


### Test Coverage Highlights
- **Ticket Validation**: Non-blank titles, allowed categories (`Network`, `Hardware`, `Software`, `Other`), allowed urgencies (`low`, `medium`, `high`), positive non-zero integers for `affected_users`.
- **Priority Calculation Engine**: Strict evaluation of Rules 1 to 4 and boundary conditions (`affected_users=10`, `affected_users=3`).
- **Assignment & Workflow**: Enforces assignment before transitioning to `in_progress`, restricts modifications on `resolved` tickets until explicitly reopened.
- **Queue Ordering**: Priority hierarchy (`critical` > `high` > `medium` > `low`) with numeric ID tie-breakers.
- **JSON Persistence**: Round-trip serialization, safe loading of empty states, error reporting on malformed JSON, and non-colliding ID generation after restart.

---

## ⚙️ Core Business Rules

### Priority Calculation Engine (Evaluated in strict order)
1. **RULE 1 — Critical**: `urgency == "high" AND affected_users >= 10`
2. **RULE 2 — High**: `urgency == "high" OR affected_users >= 10`
3. **RULE 3 — Medium**: `urgency == "medium" OR affected_users >= 3`
4. **RULE 4 — Low**: All remaining valid tickets

### Ticket Lifecycle Workflow
```
[open]  ──(Assign + Start)──>  [in_progress]  ──(Complete)──>  [resolved]
  ▲                                                                 │
  └──────────────────────────(Reopen)───────────────────────────────┘
```
- Tickets start as `open` and `unassigned`.
- A ticket **cannot** enter `in_progress` without being assigned to a staff member.
- A ticket marked `resolved` cannot be modified unless explicitly reopened back to `open`.

---

## 💾 Storage & Data Persistence

- Tickets are saved to `data/tickets.json` upon creation and updates.
- If `data/tickets.json` does not exist, CampusFlow initializes a fresh, empty workspace.
- If the file contains malformed JSON, CampusFlow displays a descriptive error rather than silently overwriting data.
- **To reset and start fresh**: Remove the data file:
  ```bash
  rm -f data/tickets.json
  ```

---

## 🔗 Pull Requests & Reviews

- **Engineer A PR (Ticket Creation & Priority Engine)**: [PR #1](https://github.com/smilinqremedy/campusflow/pull/1) *(authored by @Aocheg, reviewed by @smilinqremedy)*
- **Engineer B PR (Workflow, Queue & Reporting)**: [PR #2](https://github.com/smilinqremedy/campusflow/pull/2) *(authored by @smilinqremedy, reviewed by @Aocheg)*

---

## ⚠️ Known Limitations & Future Improvements
1. **Single-Node File Storage**: JSON file storage is optimal for local execution; concurrent processes writing to the same JSON file could encounter file-lock race conditions.
2. **Role-Based Access Control**: Staff authentication is simplified; adding role-based credentials would further strengthen assignment verification.