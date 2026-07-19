import unittest
from notifier_ok17_alpha import alpha_notifier_ok17

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_notifier_ok17(1), 2)

if __name__ == "__main__":
    unittest.main()
