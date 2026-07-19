import unittest
from ledger_ok4_base import identity_ledger_ok4

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_ledger_ok4(5), 5)

if __name__ == "__main__":
    unittest.main()
