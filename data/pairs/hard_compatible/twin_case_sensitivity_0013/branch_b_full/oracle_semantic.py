import unittest
from identity_013 import authorized_13

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_13("admin78", "Admin78"))
