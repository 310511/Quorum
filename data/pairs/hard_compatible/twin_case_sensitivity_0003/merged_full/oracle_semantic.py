import unittest
from identity_003 import authorized_3

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_3("admin18", "Admin18"))
