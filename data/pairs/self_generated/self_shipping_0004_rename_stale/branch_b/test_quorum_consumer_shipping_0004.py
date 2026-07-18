import unittest

from quorum_consumer_shipping_0004 import call_original


class Shipping0004Tests(unittest.TestCase):
    def test_consumer_is_available(self):
        self.assertTrue(callable(call_original))


if __name__ == "__main__":
    unittest.main()
