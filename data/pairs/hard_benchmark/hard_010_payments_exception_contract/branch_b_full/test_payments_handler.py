import unittest
from payments_handler import safe_payments

class HandlerTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(safe_payments(0), 0)
        self.assertEqual(safe_payments(4), 4)

if __name__ == "__main__":
    unittest.main()
