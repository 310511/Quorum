import unittest
from policy_006 import route_6

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_6(76), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_6(66), "standard")

if __name__ == "__main__":
    unittest.main()
