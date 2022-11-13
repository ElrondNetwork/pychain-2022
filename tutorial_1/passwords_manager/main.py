import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, List

import nacl.secret
import nacl.utils
from erdpy_core import Transaction
from erdpy_wallet import UserSigner, generate_pem_file

from passwords_manager import io, ux
from passwords_manager.account_key_value import AccountKeyValue
from passwords_manager.network_provider import CustomNetworkProvider
from passwords_manager.save_key_values_builder import SaveKeyValuesBuilder
from passwords_manager.secret_entry import SecretEntry


def main(cli_args: List[str]):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser("init", help="initialize passwords manager")
    sub.set_defaults(func=init)

    sub = subparsers.add_parser("add", help="create entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--wallet", required=True)
    sub.add_argument("--url", required=True)
    sub.set_defaults(func=add_entries)

    sub = subparsers.add_parser("get", help="retrieve entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--address", required=True)
    sub.add_argument("--url", required=True)
    sub.set_defaults(func=retrieve_entries)

    sub = subparsers.add_parser("update", help="update entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--wallet", required=True)
    sub.add_argument("--url", required=True)
    sub.set_defaults(func=retrieve_entries)

    sub = subparsers.add_parser("delete", help="delete entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--wallet", required=True)
    sub.add_argument("--url", required=True)
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
    secret_key = load_secret_key(Path(args.secret))
    signer = UserSigner.from_pem_file(Path(args.wallet))
    provider = create_network_provider(args.url)
    tx = create_transaction(signer, [], provider)


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


def create_transaction(signer: UserSigner, items: List[AccountKeyValue], provider: CustomNetworkProvider):
    address = signer.get_address()
    chain_id = provider.get_chain_id()
    nonce = provider.get_account_nonce(address)
    data_builder = SaveKeyValuesBuilder()
    data_builder.add_items(items)
    data = data_builder.build()
    gas_limit = compute_gas_limit(items, data.length())

    tx = Transaction(
        nonce=nonce,
        sender=address,
        receiver=address,
        gas_limit=gas_limit,
        data=data,
        chain_id=chain_id,
    )

    tx.apply_signature(signer.sign(tx))


def compute_gas_limit(items: List[AccountKeyValue], data_length: int):
    """
    See: https://docs.elrond.com/developers/account-storage/
    """
    gas_limit = 250000 + 50000
    gas_limit += 1500 * data_length

    for item in items:
        gas_limit += 10000 * len(item.key)
        gas_limit += 10000 * len(item.value)
        gas_limit += 50000 * len(item.value)

    return gas_limit


def broadcast_transaction():
    pass


def retrieve_entries(args: Any):
    print("retrieve entries")


def update_entries(args: Any):
    print("update entries")


def delete_entries(args: Any):
    print("delete entries")


def create_network_provider(url: str):
    return CustomNetworkProvider(url)


def load_secret_key(file: Path) -> bytes:
    as_hex = io.read_text(file)
    return bytes.fromhex(as_hex)


def acquire_nonce():
    pass


if __name__ == "__main__":
    return_code = main(sys.argv[1:])
    exit(return_code)
