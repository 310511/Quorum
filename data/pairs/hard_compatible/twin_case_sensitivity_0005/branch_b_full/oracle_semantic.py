import unittest
from identity_005 import authorized_5

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_5("admin30", "Admin30"))
