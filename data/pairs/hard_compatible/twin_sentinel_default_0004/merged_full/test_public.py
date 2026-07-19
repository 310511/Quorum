import unittest
from limits_004 import can_accept_4

class LimitTests(unittest.TestCase):
    def test_explicit_limit(self):
        self.assertTrue(can_accept_4(4, 10))
        self.assertFalse(can_accept_4(10, 10))

if __name__ == "__main__":
    unittest.main()
