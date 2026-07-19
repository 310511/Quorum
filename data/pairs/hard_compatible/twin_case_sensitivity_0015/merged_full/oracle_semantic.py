import unittest
from identity_015 import authorized_15

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_15("admin90", "Admin90"))
