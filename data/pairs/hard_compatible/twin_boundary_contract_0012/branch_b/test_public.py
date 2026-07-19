import unittest
from policy_012 import route_12

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_12(112), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_12(102), "standard")

if __name__ == "__main__":
    unittest.main()
