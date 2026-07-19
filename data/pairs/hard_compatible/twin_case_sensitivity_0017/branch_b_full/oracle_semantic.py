import unittest
from identity_017 import authorized_17

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_17("admin102", "Admin102"))
