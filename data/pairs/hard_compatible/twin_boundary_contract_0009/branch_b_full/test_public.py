import unittest
from policy_009 import route_9

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_9(94), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_9(84), "standard")

if __name__ == "__main__":
    unittest.main()
