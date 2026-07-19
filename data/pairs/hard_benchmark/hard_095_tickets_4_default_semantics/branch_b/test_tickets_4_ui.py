import unittest
from tickets_4_ui import preview_tickets_4

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_tickets_4()), 10)

if __name__ == "__main__":
    unittest.main()
