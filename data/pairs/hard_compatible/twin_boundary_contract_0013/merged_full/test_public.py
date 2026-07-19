import unittest
from policy_013 import route_13

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_13(118), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_13(108), "standard")

if __name__ == "__main__":
    unittest.main()
