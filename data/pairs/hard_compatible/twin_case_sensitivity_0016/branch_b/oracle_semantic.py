import unittest
from identity_016 import authorized_16

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_16("admin96", "Admin96"))
