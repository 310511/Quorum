import unittest
from payments_3_guard import ensure_payments_3_positive, Payments_3Gone

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_payments_3_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Payments_3Gone):
            ensure_payments_3_positive(0)

if __name__ == "__main__":
    unittest.main()
