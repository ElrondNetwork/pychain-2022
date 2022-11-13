import json
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, List

import nacl.secret
import nacl.utils
from erdpy_wallet import generate_pem_file

from passwords_manager import io, ux


class SecretEntry:
    def __init__(self, label: str, username: str, password: str) -> None:
        self.label = label
        self.username = username
        self.password = password

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


def main(cli_args: List[str]):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("init", help="initialize passwords manager")
    sub.set_defaults(func=init)

    sub = subparsers.add_parser("add", help="create entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--wallet", required=True)
    sub.set_defaults(func=add_entries)

    sub = subparsers.add_parser("get", help="retrieve entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--address", required=True)
    sub.set_defaults(func=retrieve_entries)

    sub = subparsers.add_parser("update", help="update entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--wallet", required=True)
    sub.set_defaults(func=retrieve_entries)

    sub = subparsers.add_parser("delete", help="delete entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--wallet", required=True)
    sub.set_defaults(func=delete_entries)

    parsed_args = parser.parse_args(cli_args)

    if not hasattr(parsed_args, "func"):
        parser.print_help()
    else:
        parsed_args.func(parsed_args)


def init(args: Any):
    path_of_wallet = Path("wallet.pem")
    path_of_secret = Path("secret.hex")

    # Generate wallet (to sign transactions)
    generate_pem_file(path_of_wallet)

    # Generate secret (for pynacl's SecretBox)
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    with open(path_of_secret, "w") as file:
        return file.write(key.hex())


def add_entries(args: Any):
    entries = ask_entries()
    secret_key = load_secret_key(args.secret)


def ask_entries():
    entries: List[SecretEntry] = []

    while True:
        if not ux.ask_confirm("Add new entry?"):
            break
        label = ux.ask_string("Label")
        username = ux.ask_string("Username")
        password = ux.ask_password("Password")

        entry = SecretEntry(label, username, password)
        entries.append(entry)


def retrieve_entries(args: Any):
    print("retrieve entries")


def update_entries(args: Any):
    print("update entries")


def delete_entries(args: Any):
    print("delete entries")


def load_secret_key(file: Path) -> bytes:
    as_hex = io.read_text(file)
    return bytes.fromhex(as_hex)


if __name__ == "__main__":
    return_code = main(sys.argv[1:])
    exit(return_code)
