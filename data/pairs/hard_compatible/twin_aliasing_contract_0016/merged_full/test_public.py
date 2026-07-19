import unittest
from records_016 import without_last_16

class RecordTests(unittest.TestCase):
    def test_result_drops_last(self):
        self.assertEqual(without_last_16([97, 98, 99]), [97, 98])

if __name__ == "__main__":
    unittest.main()
