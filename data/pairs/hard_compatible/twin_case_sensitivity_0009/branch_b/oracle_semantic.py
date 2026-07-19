import unittest
from identity_009 import authorized_9

class SemanticOracle(unittest.TestCase):
    def test_security_codes_remain_case_sensitive(self):
        self.assertFalse(authorized_9("admin54", "Admin54"))
