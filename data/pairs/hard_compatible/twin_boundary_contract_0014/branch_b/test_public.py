import unittest
from policy_014 import route_14

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_14(124), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_14(114), "standard")

if __name__ == "__main__":
    unittest.main()
