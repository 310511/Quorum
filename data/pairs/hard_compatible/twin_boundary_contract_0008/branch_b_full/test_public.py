import unittest
from policy_008 import route_8

class PolicyTests(unittest.TestCase):
    def test_clear_priority(self):
        self.assertEqual(route_8(88), "priority")
    def test_clear_standard(self):
        self.assertEqual(route_8(78), "standard")

if __name__ == "__main__":
    unittest.main()
