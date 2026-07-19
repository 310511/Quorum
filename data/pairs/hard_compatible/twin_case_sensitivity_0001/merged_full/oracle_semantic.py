import unittest
from identity_001 import authorized_1

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_1("admin6", "Admin6"))
