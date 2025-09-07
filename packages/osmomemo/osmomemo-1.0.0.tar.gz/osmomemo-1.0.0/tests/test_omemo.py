import unittest

import base64

from osmomemo import Omemo
from osmomemo import OmemoBundle
from osmomemo import XKeyPair
from osmomemo import EdKeyPair
from osmomemo.storage import OmemoStorage

class TestOmemo(unittest.TestCase):
    def test_init(self):
        storage_path = "./tests/omemo.db"
        storage = OmemoStorage(storage_path)

        bundle_a = OmemoBundle(
            676767676,
            EdKeyPair.generate(),
            XKeyPair.generate(),
            {
                "0": XKeyPair.generate(),
                "1": XKeyPair.generate(),
                "2": XKeyPair.generate(),
            }
        )

        bundle_b = OmemoBundle(
            45454545,
            EdKeyPair.generate(),
            XKeyPair.generate(),
            {
                "0": XKeyPair.generate(),
                "1": XKeyPair.generate(),
                "2": XKeyPair.generate(),
            }
        )

        omemo_a = Omemo(bundle_a, storage)
        omemo_b = Omemo(bundle_b, storage)

        message = "Initial OMEMO message (1234567890)."
        jid_b="bob@domain.com"
        device_b=45454545
        ik_b = bundle_b.get_indentity().get_public_key() 
        spk_b = bundle_b.get_prekey().get_public_key() 
        sign_b = bundle_b.get_prekey_signature(encoding=None) 
        opk_id = "0"
        opk_b = bundle_b.get_onetime_prekey(opk_id).get_public_key()
        

        EK_A, en_message = omemo_a.create_init_message(
            jid=jid_b,
            device=device_b,
            message_bytes=message.encode(),
            indentity_key=ik_b,
            signed_prekey=spk_b,
            prekey_signature=sign_b,
            onetime_prekey=opk_b,
        )

        jid_a="alice@domain.com"
        device_a=676767676
        ik_a = bundle_a.get_indentity().get_public_key() 
        ek_a = EK_A
        spk_id = "0"
        msg = en_message

        de_message = omemo_b.accept_init_message(
            jid=jid_a,
            device=device_a,
            encrypted_message=msg,
            indentity_key=ik_a,
            ephemeral_key=ek_a,
            spk_id=spk_id,
            opk_id=opk_id
        )

        self.assertEqual(message, de_message.decode())

    def test_send(self):
        storage_path = "./tests/omemo.db"
        storage = OmemoStorage(storage_path)

        bundle_a = OmemoBundle(
            676767676,
            EdKeyPair.generate(),
            XKeyPair.generate(),
            {
                "0": XKeyPair.generate(),
                "1": XKeyPair.generate(),
                "2": XKeyPair.generate(),
            }
        )

        bundle_b = OmemoBundle(
            45454545,
            EdKeyPair.generate(),
            XKeyPair.generate(),
            {
                "0": XKeyPair.generate(),
                "1": XKeyPair.generate(),
                "2": XKeyPair.generate(),
            }
        )

        omemo_a = Omemo(bundle_a, storage)
        omemo_b = Omemo(bundle_b, storage)

        message = "Initial OMEMO message (1234567890)."
        jid_b="bob@domain.com"
        device_b=bundle_b.get_device_id()
        ik_b = bundle_b.get_indentity().get_public_key() 
        spk_b = bundle_b.get_prekey().get_public_key() 
        sign_b = bundle_b.get_prekey_signature(encoding=None) 
        opk_id = "0"
        opk_b = bundle_b.get_onetime_prekey(opk_id).get_public_key()
        

        EK_A, en_message = omemo_a.create_init_message(
            jid=jid_b,
            device=device_b,
            message_bytes=message.encode(),
            indentity_key=ik_b,
            signed_prekey=spk_b,
            prekey_signature=sign_b,
            onetime_prekey=opk_b,
        )

        jid_a="alice@domain.com"
        device_a=bundle_a.get_device_id()
        ik_a = bundle_a.get_indentity().get_public_key() 
        ek_a = EK_A
        spk_id = "0"
        msg = en_message

        de_message = omemo_b.accept_init_message(
            jid=jid_a,
            device=device_a,
            encrypted_message=msg,
            indentity_key=ik_a,
            ephemeral_key=ek_a,
            spk_id=spk_id,
            opk_id=opk_id
        )

        self.assertEqual(message, de_message.decode())


        ### Sending
        ## Alice
        message_a = "Hello Bob! How are you?"

        wrapped_a, payload_a = omemo_a.send_message(jid_b, device_b, message_a.encode())

        ## Bob
        message_b = omemo_b.receive_message(jid_a, device_a, wrapped_a, payload_a)

        # TEST
        self.assertEqual(message_a, message_b.decode())


        message_b = "Hi, Alice! I am good =)"

        wrapped_b, payload_b = omemo_b.send_message(jid_a, device_a, message_b.encode())

        message_a = omemo_a.receive_message(jid_b, device_b, wrapped_b, payload_b)

        # Test
        self.assertEqual(message_b, message_a.decode())


    def test_signature(self):
        bundle = OmemoBundle(
            34059834,
            EdKeyPair.generate(),
            XKeyPair.generate(),
            {
                "0": XKeyPair.generate(),
                "1": XKeyPair.generate(),
                "2": XKeyPair.generate(),
            }
        )


        ik_b64 = bundle.get_indentity().get_base64_public_key()
        spk_b64 = bundle.get_prekey().get_base64_public_key()
        spk_sign_b64 = bundle.get_prekey_signature()

        EdKeyPair.verify_public_key(
            EdKeyPair.base64_to_public_key(ik_b64),
            XKeyPair.base64_to_public_key(spk_b64),
            base64.b64decode(spk_sign_b64.encode("utf-8")),
        )
