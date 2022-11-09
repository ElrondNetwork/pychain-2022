import datetime
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Dict, List

from bottle import route, run, static_file  # type: ignore

from deep_history.services import Services

FOLDER = Path(__file__).parent
FOLDER_STATIC = FOLDER / "static"

services = Services()


@route('/')
def index():
    return static_file("index.html", root=FOLDER)


@route('/static/<filename:path>')
def send_static(filename: Path):
    return static_file(filename, root=FOLDER_STATIC)


@route("/api/<network>/accounts/<address>/<timestamp>/native")
def get_native_state(network: str, address: str, timestamp: str):
    provider = services.get_network_provider(network)
    time = parse_time(timestamp)
    response = provider.get_native_state_of_account(address, time)
    return response


@route("/api/<network>/accounts/<address>/<timestamp>/tokens/<token>")
def get_token_state(network: str, address: str, timestamp: str, token: str):
    provider = services.get_network_provider(network)
    time = parse_time(timestamp)
    response = provider.get_token_state_of_account(address, token, time)
    return response


def parse_time(timestamp: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def main(cli_args: List[str]):
    parser = ArgumentParser()
    parser.add_argument("--port", type=int, default=30000)
    args = parser.parse_args(cli_args)

    run(host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main(sys.argv[1:])
