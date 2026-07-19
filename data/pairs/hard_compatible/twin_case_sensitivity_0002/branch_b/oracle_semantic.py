import unittest
from identity_002 import authorized_2

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_2("admin12", "Admin12"))
