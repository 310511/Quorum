import unittest
from analytics_ok5_base import identity_analytics_ok5

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_analytics_ok5(5), 5)

if __name__ == "__main__":
    unittest.main()
