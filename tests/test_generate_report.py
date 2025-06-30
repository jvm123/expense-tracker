import unittest
from pathlib import Path
import tempfile
import shutil
import csv
from expense_tracker.generate_report import calculate_month_data


class TestCalculateMonthData(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def write_csv(self, filename, rows, fieldnames):
        file_path = self.data_dir / filename
        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return file_path

    def test_basic_shared_expenses(self):
        # Main CSV
        csv_rows = [
            {
                "Date": "2025-06-01",
                "Category": "Rent",
                "Paid By": "Both",
                "Amount": "1200",
                "Notes": "",
            },
            {
                "Date": "2025-06-03",
                "Category": "Groceries",
                "Paid By": "PersonA",
                "Amount": "350",
                "Notes": "",
            },
            {
                "Date": "2025-06-05",
                "Category": "Dining Out",
                "Paid By": "PersonB",
                "Amount": "220",
                "Notes": "",
            },
        ]
        csv_file = self.write_csv(
            "2025-06.csv",
            csv_rows,
            ["Date", "Category", "Paid By", "Amount", "Notes"],
        )
        # Contributions CSV
        contrib_rows = [
            {
                "Date": "2025-06-01",
                "Name": "PersonA",
                "Amount": "1000",
                "Virtual Contribution": "No",
                "Notes": "",
            },
            {
                "Date": "2025-06-01",
                "Name": "PersonB",
                "Amount": "1000",
                "Virtual Contribution": "No",
                "Notes": "",
            },
        ]
        contrib_file = self.write_csv(
            "2025-06-contributions.csv",
            contrib_rows,
            ["Date", "Name", "Amount", "Virtual Contribution", "Notes"],
        )

        # Run calculation
        # personA contributed 1000+350, PersonB contributed 1000+220,
        # the total shared is 1770, half share is 885

        result = calculate_month_data("2025-06", csv_file, contrib_file)
        self.assertAlmostEqual(result["total_shared"], 1770.0)
        self.assertAlmostEqual(result["half_share"], 885.0)
        self.assertEqual(result["contributions"]["PersonA"], 1000.0 + 350)
        self.assertEqual(result["contributions"]["PersonB"], 1000.0 + 220)
        self.assertEqual(
            result["balances"]["PersonA"],
            result["contributions"]["PersonA"] - 885.0,
        )
        self.assertEqual(
            result["balances"]["PersonB"],
            result["contributions"]["PersonB"] - 885.0,
        )

    def test_virtual_contributions(self):
        csv_rows = [
            {
                "Date": "2025-07-01",
                "Category": "Rent",
                "Paid By": "Both",
                "Amount": "1000",
                "Notes": "",
            },
        ]
        csv_file = self.write_csv(
            "2025-07.csv",
            csv_rows,
            ["Date", "Category", "Paid By", "Amount", "Notes"],
        )
        contrib_rows = [
            {
                "Date": "2025-07-01",
                "Name": "Alice",
                "Amount": "500",
                "Virtual Contribution": "Yes",
                "Notes": "",
            },
            {
                "Date": "2025-07-01",
                "Name": "Bob",
                "Amount": "1",
                "Virtual Contribution": "No",
                "Notes": "",
            },
        ]
        contrib_file = self.write_csv(
            "2025-07-contributions.csv",
            contrib_rows,
            ["Date", "Name", "Amount", "Virtual Contribution", "Notes"],
        )
        result = calculate_month_data("2025-07", csv_file, contrib_file)
        self.assertEqual(result["virtual_contributions"]["Alice"], 500.0)
        self.assertNotIn("Bob", result.get("virtual_contributions", {}))
        self.assertIn("Alice", result.get("balances", {}))
        self.assertEqual(result["balances"]["Alice"], 0.0)
        self.assertEqual(result["balances"]["Bob"], -499.0)

    def test_no_contributions_file(self):
        csv_rows = [
            {
                "Date": "2025-08-01",
                "Category": "Rent",
                "Paid By": "Both",
                "Amount": "1000",
                "Notes": "",
            },
        ]
        csv_file = self.write_csv(
            "2025-08.csv",
            csv_rows,
            ["Date", "Category", "Paid By", "Amount", "Notes"],
        )
        # No contributions file
        result = calculate_month_data(
            "2025-08",
            csv_file,
            self.data_dir / "2025-08-contributions.csv",
        )
        self.assertIn("contributions", result)
        self.assertIn("balances", result)
        self.assertEqual(result["contributions"].get("PersonA", 0.0), 0.0)
        self.assertEqual(result["contributions"].get("PersonB", 0.0), 0.0)
        self.assertEqual(result["balances"].get("PersonA", 0.0), -500.0)
        self.assertEqual(result["balances"].get("PersonB", 0.0), -500.0)

    def test_script_equivalent(self):
        # This test mimics scripts/test_generate_report.sh logic
        csv_rows = [
            {
                "Date": "2025-09-01",
                "Category": "Rent",
                "Paid By": "Both",
                "Amount": "1200",
                "Notes": "",
            },
            {
                "Date": "2025-09-02",
                "Category": "Groceries",
                "Paid By": "PersonA",
                "Amount": "400",
                "Notes": "",
            },
            {
                "Date": "2025-09-03",
                "Category": "Utilities",
                "Paid By": "PersonB",
                "Amount": "300",
                "Notes": "",
            },
        ]
        csv_file = self.write_csv(
            "2025-09.csv",
            csv_rows,
            ["Date", "Category", "Paid By", "Amount", "Notes"],
        )
        contrib_rows = [
            {
                "Date": "2025-09-01",
                "Name": "PersonA",
                "Amount": "900",
                "Virtual Contribution": "No",
                "Notes": "",
            },
            {
                "Date": "2025-09-01",
                "Name": "PersonB",
                "Amount": "600",
                "Virtual Contribution": "No",
                "Notes": "",
            },
        ]
        contrib_file = self.write_csv(
            "2025-09-contributions.csv",
            contrib_rows,
            ["Date", "Name", "Amount", "Virtual Contribution", "Notes"],
        )
        result = calculate_month_data("2025-09", csv_file, contrib_file)
        self.assertAlmostEqual(result["total_shared"], 1900.0)
        self.assertAlmostEqual(result["half_share"], 950.0)
        self.assertEqual(result["contributions"]["PersonA"], 900.0 + 400)
        self.assertEqual(result["contributions"]["PersonB"], 600.0 + 300)
        self.assertEqual(
            result["balances"]["PersonA"],
            result["contributions"]["PersonA"] - 950.0,
        )
        self.assertEqual(
            result["balances"]["PersonB"],
            result["contributions"]["PersonB"] - 950.0,
        )


if __name__ == "__main__":
    unittest.main()
