import unittest
from analytics_ui import preview_analytics

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_analytics()), 10)

if __name__ == "__main__":
    unittest.main()
