import unittest
from identity_012 import authorized_12

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_12("admin72", "Admin72"))
