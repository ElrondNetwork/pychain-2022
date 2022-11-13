
import json
import uuid

import nacl.secret
import nacl.utils

from passwords_manager.account_key_value import AccountKeyValue


class SecretEntry:
    def __init__(self, label: str, username: str, password: str) -> None:
        self.label = label
        self.username = username
        self.password = password

    def to_key_value(self, secret_key: bytes) -> AccountKeyValue:
        key = uuid.uuid4().bytes
        value = self.encrypt(secret_key)
        return AccountKeyValue(key, value)

    def encrypt(self, secret_key: bytes) -> bytes:
        box = nacl.secret.SecretBox(secret_key)
        data = self.serialize()
        encrypted = box.encrypt(data)
        return encrypted

    def serialize(self):
        return json.dumps(self.__dict__).encode("utf-8")

    @classmethod
    def decrypt(cls, encrypted: bytes, secret_key: bytes):
        box = nacl.secret.SecretBox(secret_key)
        data = box.decrypt(encrypted)
        return cls.deserialize(data)

    @classmethod
    def deserialize(cls, serialized: bytes):
        data = json.loads(serialized.decode("utf-8"))
        return SecretEntry(data["label"], data["username"], data["password"])
