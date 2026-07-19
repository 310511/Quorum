import unittest
from cache_1_config import page_cache_1

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_cache_1(range(20)), list(range(10)))

if __name__ == "__main__":
    unittest.main()
