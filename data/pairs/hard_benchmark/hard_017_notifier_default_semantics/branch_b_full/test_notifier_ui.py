import unittest
from notifier_ui import preview_notifier

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_notifier()), 10)

if __name__ == "__main__":
    unittest.main()
