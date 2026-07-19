import unittest
from policy_005 import route_5

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_5(70), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_5(60), "standard")

if __name__ == "__main__":
    unittest.main()
