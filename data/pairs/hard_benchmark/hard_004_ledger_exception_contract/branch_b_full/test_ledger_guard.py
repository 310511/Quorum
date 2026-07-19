import unittest
from ledger_guard import ensure_ledger_positive, LedgerError

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_ledger_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(LedgerError):
            ensure_ledger_positive(0)

if __name__ == "__main__":
    unittest.main()
