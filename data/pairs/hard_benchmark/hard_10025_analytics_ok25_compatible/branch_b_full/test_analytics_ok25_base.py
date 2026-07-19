import unittest
from analytics_ok25_base import identity_analytics_ok25

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_analytics_ok25(5), 5)

if __name__ == "__main__":
    unittest.main()
