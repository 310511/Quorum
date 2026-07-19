import unittest
from ledger_ok24_alpha import alpha_ledger_ok24

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_ledger_ok24(1), 2)

if __name__ == "__main__":
    unittest.main()
