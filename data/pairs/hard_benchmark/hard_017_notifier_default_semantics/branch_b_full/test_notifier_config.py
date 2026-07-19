import unittest
from notifier_config import page_notifier

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_notifier(range(20)), list(range(10)))

if __name__ == "__main__":
    unittest.main()
