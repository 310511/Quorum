import unittest
from policy_007 import route_7

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_7(82), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_7(72), "standard")

if __name__ == "__main__":
    unittest.main()
