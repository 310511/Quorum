import unittest
from ledger_handler import safe_ledger

class HandlerTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(safe_ledger(0), 0)
        self.assertEqual(safe_ledger(4), 4)

if __name__ == "__main__":
    unittest.main()
