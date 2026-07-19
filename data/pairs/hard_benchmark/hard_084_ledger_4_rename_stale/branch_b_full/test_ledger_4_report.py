import unittest
from ledger_4_report import report_line

class ReportTests(unittest.TestCase):
    def test_report(self):
        self.assertEqual(report_line([1, 2, 3]), 12)

if __name__ == "__main__":
    unittest.main()
