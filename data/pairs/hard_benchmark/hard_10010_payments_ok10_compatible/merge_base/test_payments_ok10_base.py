import unittest
from payments_ok10_base import identity_payments_ok10

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_payments_ok10(5), 5)

if __name__ == "__main__":
    unittest.main()
