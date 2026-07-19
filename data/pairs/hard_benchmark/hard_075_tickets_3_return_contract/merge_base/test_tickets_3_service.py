import unittest
from tickets_3_service import fetch_tickets_3_record, status_of

class ServiceTests(unittest.TestCase):
    def test_record(self):
        self.assertEqual(fetch_tickets_3_record(7)["score"], 1)
    def test_status(self):
        self.assertEqual(status_of(7), "ok")

if __name__ == "__main__":
    unittest.main()
