import unittest
from ledger_ok4_beta import beta_ledger_ok4

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_ledger_ok4(3), 6)

if __name__ == "__main__":
    unittest.main()
