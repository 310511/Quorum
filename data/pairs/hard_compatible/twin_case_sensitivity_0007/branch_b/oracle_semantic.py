import unittest
from identity_007 import authorized_7

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_7("admin42", "Admin42"))
