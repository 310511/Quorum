import unittest
from tickets_3_scorecard import score_for

class ScorecardTests(unittest.TestCase):
    def test_score(self):
        self.assertEqual(score_for(3), 11)

if __name__ == "__main__":
    unittest.main()
