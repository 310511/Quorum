import unittest
from policy_004 import route_4

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_4(64), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_4(54), "standard")

if __name__ == "__main__":
    unittest.main()
