import unittest
from auth_2_config import page_auth_2

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_auth_2(range(20)), list(range(10)))

if __name__ == "__main__":
    unittest.main()
