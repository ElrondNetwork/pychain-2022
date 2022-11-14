import getpass
import json
from time import sleep
from typing import Any, Dict, Protocol

import pyperclip


class ITransaction(Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        return dict()


def ask_confirm_broadcast_transaction(tx: ITransaction) -> bool:
    pretty = json.dumps(tx.to_dictionary(), indent=4)
    print("Transaction:")
    print(pretty)
    return ask_confirm("Transaction is ready to be broadcasted, continue?")


def ask_confirm(message: str) -> bool:
    answer = input(f"{message} (y/n)")
    return answer.lower() in ["y", "yes"]


def ask_string(message: str):
    answer = input(f"{message}: ")
    return answer.strip()


def ask_number(message: str):
    answer = input(f"{message}\n")
    return int(answer)


def ask_password(message: str):
    password = getpass.getpass(f"{message}: ")
    print(f"Entered password of length {len(password)}")
    return password


def hold_in_clipboard(data: str, seconds: int = 10):
    pyperclip.copy(data)
    sleep(seconds)
    pyperclip.copy("")
