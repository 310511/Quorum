import unittest
from cache_service import fetch_cache_record, status_of

class ServiceTests(unittest.TestCase):
    def test_record(self):
        self.assertEqual(fetch_cache_record(7)["score"], 1)
    def test_status(self):
        self.assertEqual(status_of(7), "ok")

if __name__ == "__main__":
    unittest.main()
