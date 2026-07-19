import unittest
from analytics_3_config import page_analytics_3

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_analytics_3(range(20)), list(range(10)))

if __name__ == "__main__":
    unittest.main()
