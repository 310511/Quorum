import unittest
from pricing_1_config import page_pricing_1

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_pricing_1(range(20)), list(range(3)))

if __name__ == "__main__":
    unittest.main()
