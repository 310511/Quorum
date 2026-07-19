import unittest
from cache_2_api import build_cache_2_payload, summarize

class ApiTests(unittest.TestCase):
    def test_payload(self):
        self.assertEqual(build_cache_2_payload("x")["quantity"], 1)
    def test_summarize(self):
        self.assertEqual(summarize("x"), 1)

if __name__ == "__main__":
    unittest.main()
