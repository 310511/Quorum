import unittest
from auth_4_service import fetch_auth_4_record, status_of

class ServiceTests(unittest.TestCase):
    def test_record(self):
        self.assertEqual(fetch_auth_4_record(7)["meta"]["score"], 1)
    def test_status(self):
        self.assertEqual(status_of(7), "ok")

if __name__ == "__main__":
    unittest.main()
