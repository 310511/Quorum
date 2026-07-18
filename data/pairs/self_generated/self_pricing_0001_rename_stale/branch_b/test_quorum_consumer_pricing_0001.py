import unittest

from quorum_consumer_pricing_0001 import call_original


class Pricing0001Tests(unittest.TestCase):
    def test_consumer_is_available(self):
        self.assertTrue(callable(call_original))


if __name__ == "__main__":
    unittest.main()
