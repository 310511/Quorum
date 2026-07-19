import unittest
from tickets_ok15_base import identity_tickets_ok15

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_tickets_ok15(5), 5)

if __name__ == "__main__":
    unittest.main()
