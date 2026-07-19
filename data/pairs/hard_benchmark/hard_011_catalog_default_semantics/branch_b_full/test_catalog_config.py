import unittest
from catalog_config import page_catalog

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_catalog(range(20)), list(range(10)))

if __name__ == "__main__":
    unittest.main()
