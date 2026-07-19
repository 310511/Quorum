import unittest
from identity_014 import authorized_14

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_14("admin84", "Admin84"))
