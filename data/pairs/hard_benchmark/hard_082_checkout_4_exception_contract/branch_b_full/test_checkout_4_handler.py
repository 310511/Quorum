import unittest
from checkout_4_handler import safe_checkout_4

class HandlerTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(safe_checkout_4(0), 0)
        self.assertEqual(safe_checkout_4(4), 4)

if __name__ == "__main__":
    unittest.main()
