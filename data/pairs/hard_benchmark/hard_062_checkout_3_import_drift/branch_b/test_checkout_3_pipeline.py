import unittest
from checkout_3_pipeline import pipeline_key

class PipelineTests(unittest.TestCase):
    def test_key(self):
        self.assertEqual(pipeline_key(" X "), "key:x")

if __name__ == "__main__":
    unittest.main()
