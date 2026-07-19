import unittest
from identity_011 import authorized_11

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_11("admin66", "Admin66"))
