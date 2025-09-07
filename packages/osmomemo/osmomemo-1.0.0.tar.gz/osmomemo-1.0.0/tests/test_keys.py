import unittest

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey  

from osmomemo import XKeyPair
from osmomemo import EdKeyPair

class TestKeys(unittest.TestCase):
    def test_generating(self):
        xpair = XKeyPair.generate()
        edpair = EdKeyPair.generate()

        self.assertIsInstance(xpair, XKeyPair)
        self.assertIsInstance(edpair, EdKeyPair)

        self.assertIsInstance(xpair.get_private_key(), X25519PrivateKey)
        self.assertIsInstance(xpair.get_public_key(), X25519PublicKey)
        self.assertIsInstance(edpair.get_private_key(), Ed25519PrivateKey)
        self.assertIsInstance(edpair.get_public_key(), Ed25519PublicKey)


    def test_converting(self):
        edpair = EdKeyPair.generate()

        self.assertIsInstance(edpair.get_x_private_key(), X25519PrivateKey)
        self.assertIsInstance(edpair.get_x_public_key(), X25519PublicKey)


        xpair = XKeyPair(edpair.get_x_private_key())

        self.assertEqual(xpair.get_public_key(), edpair.get_x_public_key())


    def test_base64(self):
        xpair = XKeyPair.generate()
        edpair = EdKeyPair.generate()

        x_priv = xpair.get_base64_private_key()
        x_pub = xpair.get_base64_public_key()
        ed_priv = edpair.get_base64_private_key()
        ed_pub = edpair.get_base64_public_key()

        self.assertIsInstance(x_priv, str)
        self.assertIsInstance(x_pub, str)
        self.assertIsInstance(ed_priv, str)
        self.assertIsInstance(ed_pub, str)

        i_xpair = XKeyPair.import_from_base64(x_priv)
        i_edpair = EdKeyPair.import_from_base64(ed_priv)

        self.assertEqual(i_xpair.get_base64_private_key(), x_priv)
        self.assertEqual(i_xpair.get_base64_public_key(), x_pub)
        self.assertEqual(i_edpair.get_base64_private_key(), ed_priv)
        self.assertEqual(i_edpair.get_base64_public_key(), ed_pub)


        # The private ones are not the same for some reason. 
        # But if convert them to bytes, they match.
        #self.assertEqual(i_xpair.get_private_key(), xpair.get_private_key())
        self.assertEqual(i_xpair.get_public_key(), xpair.get_public_key())
        #self.assertEqual(i_edpair.get_private_key(), edpair.get_private_key())
        self.assertEqual(i_edpair.get_public_key(), edpair.get_public_key())
