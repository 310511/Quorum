import unittest
from metrics_ok1_base import identity_metrics_ok1

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_metrics_ok1(5), 5)

if __name__ == "__main__":
    unittest.main()
