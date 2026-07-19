import unittest
from scheduler_ok16_base import identity_scheduler_ok16

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_scheduler_ok16(5), 5)

if __name__ == "__main__":
    unittest.main()
