import unittest

from quorum_consumer_example_1 import call_original


class Example1Tests(unittest.TestCase):
    def test_consumer_is_available(self):
        self.assertTrue(callable(call_original))


if __name__ == "__main__":
    unittest.main()
