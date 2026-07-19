import unittest
from analytics_4_api import build_analytics_4_payload, summarize

class ApiTests(unittest.TestCase):
    def test_payload(self):
        self.assertEqual(build_analytics_4_payload("x")["quantity"], 1)
    def test_summarize(self):
        self.assertEqual(summarize("x"), 1)

if __name__ == "__main__":
    unittest.main()
