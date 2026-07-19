import unittest
from limits_012 import can_accept_12

class LimitTests(unittest.TestCase):
    def test_explicit_limit(self):
        self.assertTrue(can_accept_12(4, 10))
        self.assertFalse(can_accept_12(10, 10))

if __name__ == "__main__":
    unittest.main()
