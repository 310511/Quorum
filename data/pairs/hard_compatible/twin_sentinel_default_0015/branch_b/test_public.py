import unittest
from limits_015 import can_accept_15

class LimitTests(unittest.TestCase):
    def test_explicit_limit(self):
        self.assertTrue(can_accept_15(4, 10))
        self.assertFalse(can_accept_15(10, 10))

if __name__ == "__main__":
    unittest.main()
