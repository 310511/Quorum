import unittest
from ledger_ok4_alpha import alpha_ledger_ok4

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_ledger_ok4(1), 2)

if __name__ == "__main__":
    unittest.main()
