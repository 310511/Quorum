import unittest

from quorum_consumer_inventory_0002 import call_original


class Inventory0002Tests(unittest.TestCase):
    def test_consumer_is_available(self):
        self.assertTrue(callable(call_original))


if __name__ == "__main__":
    unittest.main()
