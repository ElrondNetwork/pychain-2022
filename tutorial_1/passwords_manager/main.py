import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, List

import nacl.secret
import nacl.utils
from erdpy_core import Address, Transaction
from erdpy_wallet import UserSigner, generate_user_pem_file

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

    sub = subparsers.add_parser("upsert", help="insert or update entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--wallet", required=True)
    sub.add_argument("--url", required=True)
    sub.set_defaults(func=upsert_entries)

    sub = subparsers.add_parser("get", help="retrieve entries")
    sub.add_argument("--secret", required=True)
    sub.add_argument("--address", required=True)
    sub.add_argument("--url", required=True)
    sub.set_defaults(func=retrieve_entries)

    parsed_args = parser.parse_args(cli_args)

    if not hasattr(parsed_args, "func"):
        parser.print_help()
    else:
        parsed_args.func(parsed_args)


def init(args: Any):
    path_of_wallet = Path("wallet.pem")
    path_of_secret = Path("secret.hex")

    # Generate wallet (to sign transactions)
    generate_user_pem_file(path_of_wallet)

    # Generate secret (for pynacl's SecretBox)
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    with open(path_of_secret, "w") as file:
        return file.write(key.hex())


def upsert_entries(args: Any):
    entries: List[SecretEntry] = ask_upsert_entries()
    if not entries:
        return

    secret_key = load_secret_key(Path(args.secret))
    pairs = [entry.to_key_value(secret_key) for entry in entries]

    signer = UserSigner.from_pem_file(Path(args.wallet))
    network_provider = create_network_provider(args.url)
    tx = create_transaction(signer, network_provider, pairs)

    if not ux.ask_confirm_broadcast_transaction(tx):
        return
    tx_hash = network_provider.send_transaction(tx)
    print("Transaction hash", tx_hash)


def ask_upsert_entries():
    entries: List[SecretEntry] = []

    while True:
        if not ux.ask_confirm("Next entry?"):
            break
        label = ux.ask_string("Label")
        username = ux.ask_string("Username")
        password = ux.ask_password("Password")

        entry = SecretEntry(label, username, password)
        entries.append(entry)

    return entries


def create_transaction(signer: UserSigner, network_provider: CustomNetworkProvider, items: List[AccountKeyValue]):
    address = signer.get_address()
    chain_id = network_provider.get_chain_id()
    nonce = network_provider.get_account_nonce(address)
    data = SaveKeyValuesBuilder().add_items(items).build()
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
    return tx


def compute_gas_limit(items: List[AccountKeyValue], data_length: int):
    """
    See: https://docs.multiversx.com/developers/account-storage/
    """
    gas_limit = 250000 + 50000
    gas_limit += 1500 * data_length

    for item in items:
        gas_limit += 1000 * len(item.key)
        gas_limit += 1000 * len(item.value)
        gas_limit += 10000 * len(item.value)

    return gas_limit


def retrieve_entries(args: Any):
    secret_key = load_secret_key(Path(args.secret))
    address = Address.from_bech32(args.address)
    network_provider = create_network_provider(args.url)
    pairs = network_provider.get_storage(address)
    entries = SecretEntry.load_many_from_storage(pairs, secret_key)
    ask_reveal_entries(entries)


def ask_reveal_entries(entries: List[SecretEntry]):
    entry = ask_choose_entry(entries)
    ask_reveal_entry(entry)


def ask_choose_entry(entries: List[SecretEntry]) -> SecretEntry:
    print("Choose one of the following entries:")

    for index, entry in enumerate(entries):
        print(f"{index}) {entry.label}")

    index = ux.ask_number("Index:")
    return entries[index]


def ask_reveal_entry(entry: SecretEntry):
    print(f"Username: {entry.username}")
    print("1) Reveal password")
    print("2) Hold password in clipboard (for a limited time)")
    choice = ux.ask_number("Pick a choice!")

    if choice == 1:
        print(f"Password: {entry.password}")
    elif choice == 2:
        ux.hold_in_clipboard(entry.password)


def create_network_provider(url: str):
    return CustomNetworkProvider(url)


def load_secret_key(file: Path) -> bytes:
    as_hex = io.read_text(file)
    return bytes.fromhex(as_hex)


if __name__ == "__main__":
    return_code = main(sys.argv[1:])
    exit(return_code)
