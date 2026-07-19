import unittest
from policy_002 import route_2

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_2(52), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_2(42), "standard")

if __name__ == "__main__":
    unittest.main()
