import unittest
from search_3_client import client_order

class ClientTests(unittest.TestCase):
    def test_order(self):
        self.assertEqual(client_order("sku")["quantity"], 5)

if __name__ == "__main__":
    unittest.main()
