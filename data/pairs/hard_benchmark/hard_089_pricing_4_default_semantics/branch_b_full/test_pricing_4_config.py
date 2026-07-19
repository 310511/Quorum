import unittest
from pricing_4_config import page_pricing_4

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_pricing_4(range(20)), list(range(10)))

if __name__ == "__main__":
    unittest.main()
