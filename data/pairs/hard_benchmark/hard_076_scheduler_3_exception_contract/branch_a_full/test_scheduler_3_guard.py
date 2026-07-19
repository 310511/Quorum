import unittest
from scheduler_3_guard import ensure_scheduler_3_positive, Scheduler_3Gone

class GuardTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(ensure_scheduler_3_positive(2), 2)
    def test_bad(self):
        with self.assertRaises(Scheduler_3Gone):
            ensure_scheduler_3_positive(0)

if __name__ == "__main__":
    unittest.main()
