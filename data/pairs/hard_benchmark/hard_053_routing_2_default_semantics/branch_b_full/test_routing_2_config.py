import unittest
from routing_2_config import page_routing_2

class ConfigTests(unittest.TestCase):
    def test_page(self):
        self.assertEqual(page_routing_2(range(20)), list(range(10)))

if __name__ == "__main__":
    unittest.main()
