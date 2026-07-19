import unittest
from notifier_ok17_base import identity_notifier_ok17

class BaseTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(identity_notifier_ok17(5), 5)

if __name__ == "__main__":
    unittest.main()
