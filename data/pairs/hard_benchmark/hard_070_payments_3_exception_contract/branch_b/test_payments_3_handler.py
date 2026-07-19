import unittest
from payments_3_handler import safe_payments_3

class HandlerTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(safe_payments_3(0), 0)
        self.assertEqual(safe_payments_3(4), 4)

if __name__ == "__main__":
    unittest.main()
