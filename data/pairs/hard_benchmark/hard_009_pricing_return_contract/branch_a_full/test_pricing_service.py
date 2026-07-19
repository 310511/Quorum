import unittest
from pricing_service import fetch_pricing_record, status_of

class ServiceTests(unittest.TestCase):
    def test_record(self):
        self.assertEqual(fetch_pricing_record(7)["meta"]["score"], 1)
    def test_status(self):
        self.assertEqual(status_of(7), "ok")

if __name__ == "__main__":
    unittest.main()
