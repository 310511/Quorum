import unittest
from metrics_2_ui import preview_metrics_2

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_metrics_2()), 10)

if __name__ == "__main__":
    unittest.main()
