import getpass
from time import sleep

import pyperclip


def ask_confirm(message: str):
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
