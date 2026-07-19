import unittest
from policy_003 import route_3

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_3(58), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_3(48), "standard")

if __name__ == "__main__":
    unittest.main()
