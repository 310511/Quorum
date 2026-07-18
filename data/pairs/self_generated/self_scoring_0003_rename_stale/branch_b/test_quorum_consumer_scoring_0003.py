import unittest

from quorum_consumer_scoring_0003 import call_original


class Scoring0003Tests(unittest.TestCase):
    def test_consumer_is_available(self):
        self.assertTrue(callable(call_original))


if __name__ == "__main__":
    unittest.main()
