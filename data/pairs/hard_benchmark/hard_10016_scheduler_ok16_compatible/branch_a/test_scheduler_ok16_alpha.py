import unittest
from scheduler_ok16_alpha import alpha_scheduler_ok16

class AlphaTests(unittest.TestCase):
    def test_alpha(self):
        self.assertEqual(alpha_scheduler_ok16(1), 2)

if __name__ == "__main__":
    unittest.main()
