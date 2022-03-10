

from django.test import TestCase
from spid_cie_oidc.provider.processors import spidCode

class ProcessorsTest(TestCase):

    def test_processors(self):
        processed = "9893261da4a1fec47a19b2cc4237d82f3eb70ddafdaad51bb61138b5126e72644c3189db53f9303cdc85cb84438caf9c07431944894b5742a1d33d111abf88c8"
        res = spidCode({"username" : "testusername"}, {})
        self.assertEqual(res, processed)
