import unittest
from cache_2_api import build_cache_2_payload, summarize

class ApiTests(unittest.TestCase):
    def test_payload(self):
        payload = build_cache_2_payload("x", quantity=2, priority="high")
        self.assertEqual(payload["quantity"], 2)
        self.assertEqual(payload["priority"], "high")
    def test_summarize(self):
        self.assertEqual(summarize("x"), 1)

if __name__ == "__main__":
    unittest.main()
