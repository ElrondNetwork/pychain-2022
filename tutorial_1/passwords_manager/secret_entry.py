
import json
import uuid
from typing import List

import nacl.secret
import nacl.utils

from passwords_manager.account_key_value import AccountKeyValue

MARKER = b"PASSWORDS_MANAGER_PYCHAIN_2022"


class SecretEntry:
    def __init__(self, label: str, username: str, password: str) -> None:
        self.label = label
        self.username = username
        self.password = password

    def to_key_value(self, secret_key: bytes) -> AccountKeyValue:
        key = MARKER + uuid.uuid4().bytes
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
    def load_many_from_storage(cls, pairs: List[AccountKeyValue], secret_key: bytes) -> List['SecretEntry']:
        entries: List[SecretEntry] = []

        for pair in pairs:
            if pair.key.startswith(MARKER):
                entry = SecretEntry.decrypt(pair.value, secret_key)
                entries.append(entry)

        return entries

    @classmethod
    def decrypt(cls, encrypted: bytes, secret_key: bytes):
        box = nacl.secret.SecretBox(secret_key)
        data = box.decrypt(encrypted)
        return cls.deserialize(data)

    @classmethod
    def deserialize(cls, serialized: bytes):
        data = json.loads(serialized.decode("utf-8"))
        return SecretEntry(data["label"], data["username"], data["password"])
