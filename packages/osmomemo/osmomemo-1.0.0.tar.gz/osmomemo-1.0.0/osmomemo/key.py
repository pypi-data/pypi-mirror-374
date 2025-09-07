import base64

from typing import Self

from cryptography.hazmat.primitives.serialization import KeySerializationEncryption 
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey  

from nacl.bindings import (
    crypto_sign_ed25519_sk_to_curve25519,
    crypto_sign_ed25519_pk_to_curve25519,
)

class XKeyPair:
    def __init__(self, private_key: X25519PrivateKey):
        self._private_key = private_key
        self._public_key = self._private_key.public_key()

    @classmethod
    def generate(cls) -> Self:
        return cls(X25519PrivateKey.generate())

    @classmethod
    def import_from_base64(cls, private_b64: str) -> Self:
        return cls(cls.base64_to_private_key(private_b64))

    @staticmethod
    def base64_to_private_key(b64: str) -> X25519PrivateKey:
        raw_bytes = base64.b64decode(b64)
        return X25519PrivateKey.from_private_bytes(raw_bytes)

    @staticmethod
    def base64_to_public_key(b64: str) -> X25519PublicKey:
        raw_bytes = base64.b64decode(b64)
        return X25519PublicKey.from_public_bytes(raw_bytes)

    @staticmethod
    def private_key_to_base64(
                private_key: X25519PrivateKey,
                encryption: KeySerializationEncryption = NoEncryption(), 
                encoding="utf-8"
            ) -> bytes | str:
        private_bytes = private_key.private_bytes(
            encoding=Encoding.Raw,
            format=PrivateFormat.Raw,
            encryption_algorithm=encryption
        )
        b64 = base64.b64encode(private_bytes)

        if (encoding):
            return b64.decode(encoding)
        return b64

    @staticmethod
    def public_key_to_base64(
                public_key: X25519PublicKey,
                encoding="utf-8"
            ) -> bytes | str:
        public_bytes = public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )
        b64 = base64.b64encode(public_bytes)

        if (encoding):
            return b64.decode(encoding)
        return b64


    def get_private_key(self) -> X25519PrivateKey:
        return self._private_key

    def get_public_key(self) -> X25519PublicKey:
        return self._public_key

    def get_base64_private_key(
                self, 
                encryption: KeySerializationEncryption = NoEncryption(), 
                encoding="utf-8"
            ) -> bytes | str:
        b64 = XKeyPair.private_key_to_base64(
                private_key=self._private_key,
                encryption=encryption,
                encoding=encoding
        )
        return b64 
        
    def get_base64_public_key(
                self, 
                encoding="utf-8"
            ) -> bytes | str:
        b64 = XKeyPair.public_key_to_base64(
                public_key=self._public_key,
                encoding=encoding
        )
        return b64 


class EdKeyPair:
    def __init__(self, private_key: Ed25519PrivateKey):
        self._private_key = private_key
        self._public_key = self._private_key.public_key()

    @classmethod
    def generate(cls) -> Self:
        return cls(Ed25519PrivateKey.generate())

    @classmethod
    def import_from_base64(cls, private_b64: str) -> Self:
        return cls(cls.base64_to_private_key(private_b64))

    @staticmethod
    def base64_to_private_key(b64: str) -> Ed25519PrivateKey:
        raw_bytes = base64.b64decode(b64)
        return Ed25519PrivateKey.from_private_bytes(raw_bytes)

    @staticmethod
    def base64_to_public_key(b64: str) -> Ed25519PublicKey:
        raw_bytes = base64.b64decode(b64)
        return Ed25519PublicKey.from_public_bytes(raw_bytes)

    @staticmethod
    def private_key_to_base64(
                private_key: Ed25519PrivateKey,
                encryption: KeySerializationEncryption = NoEncryption(), 
                encoding="utf-8"
            ) -> bytes | str:
        private_bytes = private_key.private_bytes(
            encoding=Encoding.Raw,
            format=PrivateFormat.Raw,
            encryption_algorithm=encryption
        )
        b64 = base64.b64encode(private_bytes)

        if (encoding):
            return b64.decode(encoding)
        return b64

    @staticmethod
    def public_key_to_base64(
                public_key: Ed25519PublicKey,
                encoding="utf-8"
            ) -> bytes | str:
        public_bytes = public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )
        b64 = base64.b64encode(public_bytes)

        if (encoding):
            return b64.decode(encoding)
        return b64

    @staticmethod
    def private_ed_to_x_key(private_key: Ed25519PrivateKey) -> X25519PrivateKey:
        private_bytes = private_key.private_bytes(
            encoding=Encoding.Raw,
            format=PrivateFormat.Raw,
            encryption_algorithm=NoEncryption()
        )
        public_bytes = private_key.public_key().public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )
        ed_bytes = private_bytes + public_bytes
        x_bytes = crypto_sign_ed25519_sk_to_curve25519(ed_bytes)
        return X25519PrivateKey.from_private_bytes(x_bytes)


    @staticmethod
    def public_ed_to_x_key(public_key: Ed25519PublicKey) -> X25519PublicKey:
        pyblic_bytes = public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )
        x_bytes = crypto_sign_ed25519_pk_to_curve25519(pyblic_bytes)
        return X25519PublicKey.from_public_bytes(x_bytes)


    def get_private_key(self) -> Ed25519PrivateKey:
        return self._private_key

    def get_public_key(self) -> Ed25519PublicKey:
        return self._public_key

    def get_x_private_key(self) -> X25519PrivateKey:
        return EdKeyPair.private_ed_to_x_key(self._private_key)

    def get_x_public_key(self) -> X25519PublicKey:
        return EdKeyPair.public_ed_to_x_key(self._public_key)

    def get_base64_private_key(
                self, 
                encryption: KeySerializationEncryption = NoEncryption(), 
                encoding="utf-8"
            ) -> bytes | str:
        b64 = EdKeyPair.private_key_to_base64(
                private_key=self._private_key,
                encryption=encryption,
                encoding=encoding
        )
        return b64 
        
    def get_base64_public_key(
                self, 
                encoding="utf-8"
            ) -> bytes | str:
        b64 = EdKeyPair.public_key_to_base64(
                public_key=self._public_key,
                encoding=encoding
        )
        return b64 

    def sign_public_key(
                self, 
                public_key: X25519PublicKey | Ed25519PublicKey, 
                encoding="utf-8"
            ) -> bytes | str:
        sign_bytes = self._private_key.sign(public_key.public_bytes(Encoding.Raw, PublicFormat.Raw))

        if (encoding):
            return base64.b64encode(sign_bytes).decode(encoding)
        return sign_bytes 


    @staticmethod
    def verify_public_key(
                verifier: Ed25519PublicKey, 
                public_key: X25519PublicKey | Ed25519PublicKey, 
                signature: bytes,
            ):
        verifier.verify(signature, public_key.public_bytes(Encoding.Raw, PublicFormat.Raw))

