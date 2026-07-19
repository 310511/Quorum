import unittest
from policy_010 import route_10

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_10(100), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_10(90), "standard")

if __name__ == "__main__":
    unittest.main()
