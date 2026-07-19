import unittest
from policy_011 import route_11

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_11(106), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_11(96), "standard")

if __name__ == "__main__":
    unittest.main()
