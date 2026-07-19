import unittest
from notifier_ok17_beta import beta_notifier_ok17

class BetaTests(unittest.TestCase):
    def test_beta(self):
        self.assertEqual(beta_notifier_ok17(3), 6)

if __name__ == "__main__":
    unittest.main()
