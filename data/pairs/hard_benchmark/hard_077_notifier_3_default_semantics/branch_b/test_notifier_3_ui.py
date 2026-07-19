import unittest
from notifier_3_ui import preview_notifier_3

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_notifier_3()), 10)

if __name__ == "__main__":
    unittest.main()
