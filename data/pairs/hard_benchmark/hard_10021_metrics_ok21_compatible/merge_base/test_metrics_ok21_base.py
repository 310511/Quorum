import unittest
from metrics_ok21_base import identity_metrics_ok21

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_metrics_ok21(5), 5)

if __name__ == "__main__":
    unittest.main()
