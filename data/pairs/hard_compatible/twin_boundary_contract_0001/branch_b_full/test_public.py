import unittest
from policy_001 import route_1

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_1(46), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_1(36), "standard")

if __name__ == "__main__":
    unittest.main()
