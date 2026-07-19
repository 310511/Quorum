import unittest
from policy_016 import route_16

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_16(136), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_16(126), "standard")

if __name__ == "__main__":
    unittest.main()
