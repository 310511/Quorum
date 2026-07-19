import unittest
from analytics_config import page_analytics

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_analytics(range(20)), list(range(10)))

if __name__ == "__main__":
    unittest.main()
