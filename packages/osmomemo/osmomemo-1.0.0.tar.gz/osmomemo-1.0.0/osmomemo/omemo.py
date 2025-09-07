import os
import json
import base64

from typing import Tuple, List

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey  

from .bundle import OmemoBundle
from .storage import OmemoStorage
from .key import XKeyPair, EdKeyPair 
from .crypto import OmemoCryptography as OmemoCrypto

def b64(b: bytes) -> str:
    return base64.b64encode(b).decode('utf-8')

def ub64(s: str) -> bytes:
    return base64.b64decode(s.encode("utf-8"))

class Omemo:
    def __init__(self, bundle: OmemoBundle, storage: OmemoStorage):
        self._bundle = bundle
        self._storage = storage

    def get_device_list(self, jid) -> List[int] | None:
        try:
            return self._storage.get_device_list(jid)
        except:
            return None

    def create_init_message(
                self,
                jid: str,
                device: int,
                message_bytes: bytes,
                indentity_key: Ed25519PublicKey,
                signed_prekey: X25519PublicKey,
                prekey_signature: bytes,
                onetime_prekey: X25519PublicKey,
            ) -> Tuple[bytes, bytes, bytes]:
        # Key pairs
        indentity_pair = self._bundle.get_indentity()

        SK, ek_pub, encrypted_message = OmemoCrypto.create_init_message(
                message_bytes=message_bytes,
                indentity_pair=indentity_pair,
                indentity_key=indentity_key,
                signed_prekey=signed_prekey,
                prekey_signature=prekey_signature,
                onetime_prekey=onetime_prekey,
        )

        SK_RECV, SK_SEND = OmemoCrypto.split_secret_key(SK)

        self._storage.add_device(jid, device)
        self._storage.add_session(jid, device, b64(SK_RECV), b64(SK_SEND))

        return ek_pub, encrypted_message 

    def accept_init_message(
                self,
                jid: str,
                device: int,
                encrypted_message: bytes,
                indentity_key: Ed25519PublicKey,
                ephemeral_key: X25519PublicKey,
                spk_id: str,
                opk_id: str,
            ) -> Tuple[bytes, bytes]:

        # Key pairs
        indentity_pair = self._bundle.get_indentity()
        prekey_pair = self._bundle.get_prekey()
        onetime_prekey_pair = self._bundle.get_onetime_prekey(opk_id)
        
        SK, message_bytes = OmemoCrypto.accept_init_message(
                encrypted_message=encrypted_message,
                indentity_pair=indentity_pair,
                prekey_pair=prekey_pair,
                onetime_prekey_pair=onetime_prekey_pair,
                indentity_key=indentity_key,
                ephemeral_key=ephemeral_key,
        )

        SK_SEND, SK_RECV = OmemoCrypto.split_secret_key(SK)

        self._storage.add_device(jid, device)
        self._storage.add_session(jid, device, b64(SK_RECV), b64(SK_SEND))

        return message_bytes

    def send_message(self, jid: str, device: int, message_bytes: bytes) -> Tuple[bytes, bytes, bytes]:
        session = self._storage.get_session(jid, device)
        next_ck, wrapped, payload = OmemoCrypto.send_message(
                ub64(session.send_secret_key), 
                session.send_count, 
                message_bytes
        )
        self._storage.update_send_secret(jid, device, b64(next_ck))
        self._storage.increase_send_count(jid, device)
        return wrapped, payload

    def receive_message(self, jid: str, device: int, wrapped_message_key: bytes, payload: bytes) -> Tuple[bytes, bytes, bytes]:
        session = self._storage.get_session(jid, device)
        next_ck, message = OmemoCrypto.receive_message(
                ub64(session.receive_secret_key), 
                session.receive_count, 
                wrapped_message_key, 
                payload
        )
        self._storage.update_receive_secret(jid, device, b64(next_ck))
        self._storage.increase_receive_count(jid, device)
        return message

    def close_storage(self):
        pass
