import unittest
from routing_ok13_base import identity_routing_ok13

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_routing_ok13(5), 5)

if __name__ == "__main__":
    unittest.main()
