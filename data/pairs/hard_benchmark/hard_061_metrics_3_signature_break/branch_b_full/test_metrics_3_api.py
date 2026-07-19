import unittest
from metrics_3_api import build_metrics_3_payload, summarize

class ApiTests(unittest.TestCase):
    def test_payload(self):
        self.assertEqual(build_metrics_3_payload("x")["quantity"], 1)
    def test_summarize(self):
        self.assertEqual(summarize("x"), 1)

if __name__ == "__main__":
    unittest.main()
