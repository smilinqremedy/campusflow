import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, change_status
from campusflow.reports import work_queue, build_report

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(
            "Wi-Fi",
            "Network",
            "high",
            12,
            existing_tickets=self.tickets,
        )
        create_ticket(
            "Printer",
            "Hardware",
            "low",
            1,
            existing_tickets=self.tickets,
        )

    def test_unassigned_ticket_cannot_start(self):
        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_assigned_ticket_lifecycle_and_reopen(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Grace")
        change_status(self.tickets, "T001", "open")
        assign_ticket(self.tickets, "T001", "Grace")
        self.assertEqual(self.tickets[0]["assigned_to"], "Grace")

    def test_blank_staff_name_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", " ")

    def test_queue_priority_then_numeric_id(self):
        # T001 critical sorts before T002 low.
        self.assertEqual([t["id"] for t in work_queue(self.tickets)], ["T001", "T002"])

    def test_resolved_ticket_excluded_from_queue(self):
        assign_ticket(self.tickets, "T001", "Ada")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        self.assertEqual([t["id"] for t in work_queue(self.tickets)], ["T002"])

    def test_empty_report(self):
        report = build_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(sum(report["by_status"].values()), 0)
        self.assertEqual(sum(report["by_priority"].values()), 0)


if __name__ == "__main__":
    unittest.main()
