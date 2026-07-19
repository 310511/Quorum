import unittest
from identity_004 import authorized_4

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_4("admin24", "Admin24"))
