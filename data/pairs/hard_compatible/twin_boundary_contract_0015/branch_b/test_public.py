import unittest
from policy_015 import route_15

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_15(130), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_15(120), "standard")

if __name__ == "__main__":
    unittest.main()
