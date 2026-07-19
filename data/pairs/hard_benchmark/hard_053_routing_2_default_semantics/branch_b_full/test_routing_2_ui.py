import unittest
from routing_2_ui import preview_routing_2

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_routing_2()), 10)

if __name__ == "__main__":
    unittest.main()
