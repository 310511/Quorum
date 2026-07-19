import unittest
from tickets_4_config import page_tickets_4

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_tickets_4(range(20)), list(range(3)))

if __name__ == "__main__":
    unittest.main()
