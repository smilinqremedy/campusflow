"""Automated tests for JSON persistence and reload integrity (Feature F7)."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket


class TestStorage(unittest.TestCase):
    """Test suite for ticket storage operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "test_tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_list_for_fresh_start(self):
        non_existent_path = Path(self.temp_dir.name) / "non_existent.json"
        tickets = load_tickets(non_existent_path)
        self.assertEqual(tickets, [])

    def test_save_and_reload_preserves_tickets(self):
        initial_tickets = []
        t1 = create_ticket("Wi-Fi failure", "Network", "high", 15, existing_tickets=initial_tickets)
        t2 = create_ticket("Broken trackpad", "Hardware", "low", 1, existing_tickets=initial_tickets)

        save_tickets(initial_tickets, self.file_path)
        self.assertTrue(self.file_path.exists())

        loaded_tickets = load_tickets(self.file_path)
        self.assertEqual(len(loaded_tickets), 2)
        self.assertEqual(loaded_tickets[0]["id"], "T001")
        self.assertEqual(loaded_tickets[0]["priority"], "critical")
        self.assertEqual(loaded_tickets[1]["id"], "T002")
        self.assertEqual(loaded_tickets[1]["priority"], "low")

    def test_create_ticket_after_reload_maintains_unique_ids(self):
        initial_tickets = []
        create_ticket("Keyboard issue", "Hardware", "low", 1, existing_tickets=initial_tickets)
        create_ticket("Screen flicker", "Hardware", "medium", 2, existing_tickets=initial_tickets)
        save_tickets(initial_tickets, self.file_path)

        # Simulate fresh process startup / restart
        reloaded_tickets = load_tickets(self.file_path)
        self.assertEqual(len(reloaded_tickets), 2)

        # Create new ticket in the restarted session
        t3 = create_ticket("License expired", "Software", "high", 5, existing_tickets=reloaded_tickets)
        self.assertEqual(t3["id"], "T003")

        # IDs must remain completely unique
        all_ids = [t["id"] for t in reloaded_tickets]
        self.assertEqual(all_ids, ["T001", "T002", "T003"])
        self.assertEqual(len(all_ids), len(set(all_ids)))

    def test_malformed_json_raises_clear_storage_error(self):
        # Write corrupted JSON
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json [")

        with self.assertRaises(StorageError) as ctx:
            load_tickets(self.file_path)

        self.assertIn("Storage corruption detected", str(ctx.exception))
        self.assertIn("Malformed JSON", str(ctx.exception))

    def test_non_list_json_raises_storage_error(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump({"not_a": "list"}, f)

        with self.assertRaises(StorageError) as ctx:
            load_tickets(self.file_path)

        self.assertIn("Root element must be a list", str(ctx.exception))

    def test_creates_nested_directories_on_save(self):
        nested_path = Path(self.temp_dir.name) / "nested" / "sub" / "data.json"
        save_tickets([{"id": "T001"}], nested_path)
        self.assertTrue(nested_path.exists())
        loaded = load_tickets(nested_path)
        self.assertEqual(len(loaded), 1)


if __name__ == "__main__":
    unittest.main()
