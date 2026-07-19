import unittest
from scheduler_guard import ensure_scheduler_positive, SchedulerError

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_scheduler_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(SchedulerError):
            ensure_scheduler_positive(0)

if __name__ == "__main__":
    unittest.main()
