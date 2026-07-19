import unittest
from metrics_2_config import page_metrics_2

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_metrics_2(range(20)), list(range(3)))

if __name__ == "__main__":
    unittest.main()
