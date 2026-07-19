import unittest
from ledger_ok24_base import identity_ledger_ok24

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_ledger_ok24(5), 5)

if __name__ == "__main__":
    unittest.main()
