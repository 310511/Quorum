import unittest
from search_2_config import page_search_2

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_search_2(range(20)), list(range(3)))

if __name__ == "__main__":
    unittest.main()
