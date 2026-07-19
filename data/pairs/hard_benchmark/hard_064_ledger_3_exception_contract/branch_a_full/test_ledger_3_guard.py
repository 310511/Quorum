import unittest
from ledger_3_guard import ensure_ledger_3_positive, Ledger_3Gone

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_ledger_3_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Ledger_3Gone):
            ensure_ledger_3_positive(0)

if __name__ == "__main__":
    unittest.main()
