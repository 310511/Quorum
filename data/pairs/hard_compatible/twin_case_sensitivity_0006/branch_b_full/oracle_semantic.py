import unittest
from identity_006 import authorized_6

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_6("admin36", "Admin36"))
