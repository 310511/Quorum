import unittest
from scheduler_handler import safe_scheduler

class HandlerTests(unittest.TestCase):
    def test_safe(self):
        self.assertEqual(safe_scheduler(0), 0)
        self.assertEqual(safe_scheduler(4), 4)

if __name__ == "__main__":
    unittest.main()
