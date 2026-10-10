"""Unit tests for ticket creation, validation, and priority engine.

Authored by Engineer A (Oche Gabriel Adanu).
"""

import unittest
from campusflow.tickets import (
    ALLOWED_CATEGORIES,
    ALLOWED_URGENCIES,
    calculate_priority,
    create_ticket,
    format_ticket_details,
    format_ticket_summary,
    generate_ticket_id,
    get_ticket_by_id,
    is_valid_ticket_id,
    validate_ticket_inputs,
)



class TestTicketValidation(unittest.TestCase):
    """Test suite for ticket input validation and normalization."""

    def test_valid_inputs_are_normalized(self):
        title, cat, urg, users = validate_ticket_inputs(
            title="  Campus Wi-Fi is down  ",
            category="network",
            urgency="HIGH",
            affected_users=15
        )
        self.assertEqual(title, "Campus Wi-Fi is down")
        self.assertEqual(cat, "Network")
        self.assertEqual(urg, "high")
        self.assertEqual(users, 15)

    def test_blank_title_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            validate_ticket_inputs("   ", "Network", "high", 5)
        self.assertIn("must not be blank", str(ctx.exception))

    def test_non_string_title_raises_type_error(self):
        with self.assertRaises(TypeError):
            validate_ticket_inputs(123, "Network", "high", 5)

    def test_invalid_category_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            validate_ticket_inputs("Power glitch", "Electrical", "low", 2)
        self.assertIn("Invalid category", str(ctx.exception))

    def test_all_allowed_categories_accepted_case_insensitively(self):
        for cat in ALLOWED_CATEGORIES:
            _, normalized_cat, _, _ = validate_ticket_inputs(
                "Printer jammed", cat.lower(), "low", 1
            )
            self.assertEqual(normalized_cat, cat)

    def test_invalid_urgency_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            validate_ticket_inputs("Broken key", "Hardware", "extreme", 1)
        self.assertIn("Invalid urgency", str(ctx.exception))

    def test_all_allowed_urgencies_accepted(self):
        for urg in ALLOWED_URGENCIES:
            _, _, normalized_urg, _ = validate_ticket_inputs(
                "Software license expired", "Software", urg.upper(), 1
            )
            self.assertEqual(normalized_urg, urg)

    def test_zero_affected_users_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_ticket_inputs("No one affected", "Other", "low", 0)
        self.assertIn("greater than zero", str(ctx.exception))

    def test_negative_affected_users_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            validate_ticket_inputs("Negative test", "Other", "low", -3)
        self.assertIn("greater than zero", str(ctx.exception))

    def test_non_integer_affected_users_rejected(self):
        # Floats, strings, and booleans should be rejected
        for invalid_val in [2.5, "10", True, False, None]:
            with self.subTest(val=invalid_val):
                with self.assertRaises((ValueError, TypeError)):
                    validate_ticket_inputs("Issue", "Network", "medium", invalid_val)


class TestPriorityCalculationEngine(unittest.TestCase):
    """Test suite for priority calculation rules (Section 1.3)."""

    def test_rule1_high_urgency_and_10_or_more_users_is_critical(self):
        # Boundary cases: 10, 12, 100
        self.assertEqual(calculate_priority("high", 10), "critical")
        self.assertEqual(calculate_priority("high", 12), "critical")
        self.assertEqual(calculate_priority("high", 50), "critical")

    def test_rule2_high_urgency_or_10_or_more_users_is_high(self):
        # High urgency with fewer than 10 users
        self.assertEqual(calculate_priority("high", 2), "high")
        self.assertEqual(calculate_priority("high", 9), "high")
        # 10 or more users with low or medium urgency
        self.assertEqual(calculate_priority("low", 10), "high")
        self.assertEqual(calculate_priority("medium", 15), "high")

    def test_rule3_medium_urgency_or_3_or_more_users_is_medium(self):
        # Medium urgency with fewer than 3 users
        self.assertEqual(calculate_priority("medium", 1), "medium")
        self.assertEqual(calculate_priority("medium", 2), "medium")
        # Low urgency with 3 to 9 users
        self.assertEqual(calculate_priority("low", 3), "medium")
        self.assertEqual(calculate_priority("low", 4), "medium")
        self.assertEqual(calculate_priority("low", 9), "medium")

    def test_rule4_remaining_valid_tickets_is_low(self):
        # Low urgency with 1 or 2 users
        self.assertEqual(calculate_priority("low", 1), "low")
        self.assertEqual(calculate_priority("low", 2), "low")


class TestTicketCreationAndLookup(unittest.TestCase):
    """Test suite for ticket creation, unique ID generation, and lookup."""

    def test_create_ticket_structure_and_defaults(self):
        tickets = []
        ticket = create_ticket(
            title="Campus Wi-Fi is down",
            category="Network",
            urgency="high",
            affected_users=15,
            existing_tickets=tickets
        )
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["title"], "Campus Wi-Fi is down")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 15)
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0], ticket)

    def test_sequential_id_generation(self):
        tickets = []
        t1 = create_ticket("Issue 1", "Hardware", "low", 1, tickets)
        t2 = create_ticket("Issue 2", "Software", "medium", 2, tickets)
        t3 = create_ticket("Issue 3", "Other", "high", 10, tickets)
        self.assertEqual(t1["id"], "T001")
        self.assertEqual(t2["id"], "T002")
        self.assertEqual(t3["id"], "T003")

    def test_generate_ticket_id_handles_gaps_without_collision(self):
        # If tickets T001 and T003 exist, next must be T004, not T003
        gapped_tickets = [{"id": "T001"}, {"id": "T003"}]
        next_id = generate_ticket_id(gapped_tickets)
        self.assertEqual(next_id, "T004")

    def test_get_ticket_by_id(self):
        tickets = [
            {"id": "T001", "title": "First ticket"},
            {"id": "T002", "title": "Second ticket"},
        ]
        self.assertEqual(get_ticket_by_id(tickets, "T001")["title"], "First ticket")
        self.assertEqual(get_ticket_by_id(tickets, "t002")["title"], "Second ticket")
        self.assertIsNone(get_ticket_by_id(tickets, "T999"))


class TestTicketFormattingAndHelpers(unittest.TestCase):
    """Test suite for ticket display formatting and ID validation helpers."""

    def test_is_valid_ticket_id(self):
        self.assertTrue(is_valid_ticket_id("T001"))
        self.assertTrue(is_valid_ticket_id("t045"))
        self.assertTrue(is_valid_ticket_id("  T9999  "))
        self.assertFalse(is_valid_ticket_id("T01"))      # fewer than 3 digits
        self.assertFalse(is_valid_ticket_id("001"))      # missing prefix
        self.assertFalse(is_valid_ticket_id("TX01"))     # non-numeric
        self.assertFalse(is_valid_ticket_id(123))        # non-string

    def test_format_ticket_summary(self):
        ticket = {
            "id": "T001",
            "title": "Wi-Fi is down",
            "category": "Network",
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        }
        summary = format_ticket_summary(ticket)
        self.assertIn("[T001]", summary)
        self.assertIn("Wi-Fi is down", summary)
        self.assertIn("CRITICAL", summary)
        self.assertIn("Unassigned", summary)

    def test_format_ticket_details(self):
        ticket = {
            "id": "T002",
            "title": "Broken screen",
            "category": "Hardware",
            "urgency": "high",
            "affected_users": 1,
            "priority": "high",
            "status": "in_progress",
            "assigned_to": "Fredrick",
        }
        details = format_ticket_details(ticket)
        self.assertIn("Ticket ID:       T002", details)
        self.assertIn("Category:        Hardware", details)
        self.assertIn("Priority:        HIGH", details)
        self.assertIn("Status:          in_progress", details)
        self.assertIn("Assigned To:     Fredrick", details)


if __name__ == "__main__":
    unittest.main()

