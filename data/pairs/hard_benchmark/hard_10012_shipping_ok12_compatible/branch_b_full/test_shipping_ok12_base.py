import unittest
from shipping_ok12_base import identity_shipping_ok12

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_shipping_ok12(5), 5)

if __name__ == "__main__":
    unittest.main()
