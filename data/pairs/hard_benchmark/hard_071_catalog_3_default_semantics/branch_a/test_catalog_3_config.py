import unittest
from catalog_3_config import page_catalog_3

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_catalog_3(range(20)), list(range(3)))

if __name__ == "__main__":
    unittest.main()
