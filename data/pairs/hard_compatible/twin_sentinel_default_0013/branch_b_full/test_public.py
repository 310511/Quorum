import unittest
from limits_013 import can_accept_13

class LimitTests(unittest.TestCase):
    def test_explicit_limit(self):
        self.assertTrue(can_accept_13(4, 10))
        self.assertFalse(can_accept_13(10, 10))

if __name__ == "__main__":
    unittest.main()
