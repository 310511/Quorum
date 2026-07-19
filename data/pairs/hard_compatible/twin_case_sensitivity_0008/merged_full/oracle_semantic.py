import unittest
from identity_008 import authorized_8

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_8("admin48", "Admin48"))
