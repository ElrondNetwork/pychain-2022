import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, List

import nacl.secret
import nacl.utils
from erdpy_wallet import generate_pem_file


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

    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    box = nacl.secret.SecretBox(key)
    encrypted = box.encrypt(b"important secret")
    plaintext = box.decrypt(encrypted)
    print(plaintext)


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
    print("add entries")


def retrieve_entries(args: Any):
    print("retrieve entries")


def update_entries(args: Any):
    print("update entries")


def delete_entries(args: Any):
    print("delete entries")


if __name__ == "__main__":
    return_code = main(sys.argv[1:])
    exit(return_code)
