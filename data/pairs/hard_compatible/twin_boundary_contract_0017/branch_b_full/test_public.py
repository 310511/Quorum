import unittest
from policy_017 import route_17

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_17(142), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_17(132), "standard")

if __name__ == "__main__":
    unittest.main()
