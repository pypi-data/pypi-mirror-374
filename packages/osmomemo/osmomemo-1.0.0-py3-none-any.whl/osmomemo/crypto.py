import os
import json

from typing import Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey  

from .key import XKeyPair, EdKeyPair 
from .bundle import OmemoBundle

class OmemoCryptography:
    @staticmethod
    def create_init_message(
                message_bytes: bytes,
                indentity_pair: EdKeyPair,
                indentity_key: Ed25519PublicKey,
                signed_prekey: X25519PublicKey,
                prekey_signature: bytes,
                onetime_prekey: X25519PublicKey,
            ) -> Tuple[bytes, bytes, bytes]:

        # Verify signed PreKey signature
        EdKeyPair.verify_public_key(
                verifier=indentity_key,
                public_key=signed_prekey,
                signature=prekey_signature
        )

        # We are the initiator, so we must generate a ephemeral key
        ephemeral_pair = XKeyPair.generate()

        # Private keys
        ik = indentity_pair.get_x_private_key()
        ek = ephemeral_pair.get_private_key()  

        # Make Elliptic Curve Diffie-Hellman parts
        DH1 = ik.exchange(signed_prekey)
        DH2 = ek.exchange(EdKeyPair.public_ed_to_x_key(indentity_key))
        DH3 = ek.exchange(signed_prekey)
        DH4 = ek.exchange(onetime_prekey)

        # Calculate Secret Key
        SK = OmemoCryptography._hkdf_derive(DH1 + DH2 + DH3 + DH4) 

        # Delete ephemeral
        ek_pub = ephemeral_pair.get_public_key()
        del ephemeral_pair  
        del ek

        # Derive an AEAD key and encrypt the initial payload
        aead_key = OmemoCryptography._hkdf_derive(SK)
        aesgcm = AESGCM(aead_key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, message_bytes, None)
        encrypted_message = nonce + ct

        return SK, ek_pub, encrypted_message 

    @staticmethod
    def accept_init_message(
                encrypted_message: bytes,
                indentity_pair: EdKeyPair,
                prekey_pair: XKeyPair,
                onetime_prekey_pair: XKeyPair,
                indentity_key: Ed25519PublicKey,
                ephemeral_key: X25519PublicKey,
            ) -> Tuple[bytes, bytes]:
        
        # Private keys
        ik = indentity_pair.get_x_private_key()
        spk = prekey_pair.get_private_key()
        opk = onetime_prekey_pair.get_private_key()

        # Make Elliptic Curve Diffie-Hellman parts
        DH1 = spk.exchange(EdKeyPair.public_ed_to_x_key(indentity_key))
        DH2 = ik.exchange(ephemeral_key)
        DH3 = spk.exchange(ephemeral_key)
        DH4 = opk.exchange(ephemeral_key)

        # Calculate Secret Key
        SK = OmemoCryptography._hkdf_derive(DH1 + DH2 + DH3 + DH4) 

        # Derive an AEAD key and encrypt the initial payload
        aead_key = OmemoCryptography._hkdf_derive(SK)
        aesgcm = AESGCM(aead_key)
        nonce = encrypted_message[:12]; 
        ct = encrypted_message[12:]
        message_bytes = aesgcm.decrypt(nonce, ct, None)

        return SK, message_bytes

    @staticmethod
    def split_secret_key(secret_key) -> Tuple[bytes, bytes]:
        two_cks = OmemoCryptography._hkdf_derive(secret_key, length=64)
        return two_cks[32:], two_cks[:32]

    @staticmethod
    def send_message(chain_key, count, message_bytes) -> Tuple[bytes, bytes, bytes]:
        msg_key, wrap_key, next_ck = OmemoCryptography._derive_message_and_wrap(chain_key, count)
        wrapped = OmemoCryptography._wrap_message_key(wrap_key, msg_key)
        payload = OmemoCryptography._encrypt_payload_with_msgkey(msg_key, message_bytes)
        return next_ck, wrapped, payload

    @staticmethod
    def receive_message(chain_key, count, wrapped_message_key, payload) -> Tuple[bytes, bytes, bytes]:
        _, wrap_key, next_ck = OmemoCryptography._derive_message_and_wrap(chain_key, count)
        message_key = OmemoCryptography._unwrap_message_key(wrap_key, wrapped_message_key)
        message = OmemoCryptography._decrypt_payload_with_msgkey(message_key, payload)
        return next_ck, message



    @staticmethod
    def _hkdf_derive(kbs, info=b"OMEMO X3DH", length=32, salt=None) -> bytes:
        hk = HKDF(algorithm=hashes.SHA256(), info=info, length=length, salt=salt)
        return hk.derive(kbs)

    @staticmethod
    def _derive_message_and_wrap(ck, counter) -> Tuple[bytes, bytes, bytes]:
        ctr_bytes = counter.to_bytes(8, 'big')
        msg_key = OmemoCryptography._hkdf_derive(ck, info=b"msg|" + ctr_bytes, length=32)
        wrap_key = OmemoCryptography._hkdf_derive(ck, info=b"wrap", length=32)
        new_ck = OmemoCryptography._hkdf_derive(ck, info=b"ck", length=32)
        return msg_key, wrap_key, new_ck

    @staticmethod
    def _wrap_message_key(wrap_key, message_key) -> bytes:
        aes = AESGCM(wrap_key)
        nonce = os.urandom(12)
        ct = aes.encrypt(nonce, message_key, None)
        return nonce + ct

    @staticmethod
    def _unwrap_message_key(wrap_key, message_key) -> bytes:
        nonce, ct = message_key[:12], message_key[12:]
        aes = AESGCM(wrap_key)
        return aes.decrypt(nonce, ct, None)

    @staticmethod
    def _encrypt_payload_with_msgkey(message_key, message_bytes) -> bytes:
        aes = AESGCM(message_key)
        nonce = os.urandom(12)
        ct = aes.encrypt(nonce, message_bytes, None)
        return nonce + ct

    @staticmethod
    def _decrypt_payload_with_msgkey(message_key, payload) -> bytes:
        nonce, ct = payload[:12], payload[12:]
        aes = AESGCM(message_key)
        return aes.decrypt(nonce, ct, None)



