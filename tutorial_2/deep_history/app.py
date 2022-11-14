import datetime
import os
from pathlib import Path
from typing import Any

from bottle import static_file  # type: ignore
from bottle import Bottle, request, response  # type: ignore
from erdpy_network.errors import GenericError

from deep_history.network_provider import CustomNetworkProvider
from deep_history.services import Services

FOLDER = Path(__file__).parent
FOLDER_STATIC = FOLDER / "static"


class RequestError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def handle_error(func: Any):
    def wrapper(*args: Any, **kwargs: Any):
        try:
            return func(*args, **kwargs)
        except RequestError as err:
            return dict(error=str(err), status_code=400)
        except GenericError as err:
            return dict(error=str(err), status_code=500)
        except Exception as err:
            return dict(error=str(err), status_code=500)

    return wrapper


services = Services(
    mainnet_provider=CustomNetworkProvider(
        url=os.environ.get("MAINNET_GATEWAY", ""),
        username=os.environ.get("HTTP_BASIC_USERNAME_MAINNET"),
        password=os.environ.get("HTTP_BASIC_PASSWORD_MAINNET")
    ),
    devnet_provider=CustomNetworkProvider(
        url=os.environ.get("DEVNET_GATEWAY", ""),
        username=os.environ.get("HTTP_BASIC_USERNAME_DEVNET"),
        password=os.environ.get("HTTP_BASIC_PASSWORD_DEVNET")
    )
)

app: Any = Bottle()


@app.route('/')
def index():
    return static_file("index.html", root=FOLDER)


@app.route('/static/<filename:path>')
def send_static(filename: Path):
    return static_file(filename, root=FOLDER_STATIC)


@app.route("/api/<network>/accounts/<address>/native")
@handle_error
def get_native_balance(network: str, address: str):
    time, block_nonce = parse_query_parameters()
    provider = services.get_network_provider(network)
    response = provider.get_native_balance(address, time, block_nonce)
    return response.to_dictionary()


@app.route("/api/<network>/accounts/<address>/token/<token>")
@handle_error
def get_token_balance(network: str, address: str, token: str):
    time, block_nonce = parse_query_parameters()
    provider = services.get_network_provider(network)
    response = provider.get_token_balance(address, token, time, block_nonce)
    return response.to_dictionary()


@app.route("/api/<network>/accounts/<address>/storage")
@handle_error
def get_whole_storage(network: str, address: str):
    time, block_nonce = parse_query_parameters()
    provider = services.get_network_provider(network)
    response = provider.get_whole_storage(address, time, block_nonce)
    return response.to_dictionary()


@app.route("/api/<network>/accounts/<address>/storage/<key>")
@handle_error
def get_storage_entry(network: str, address: str, key: str):
    time, block_nonce = parse_query_parameters()
    provider = services.get_network_provider(network)
    response = provider.get_storage_entry(address, key, time, block_nonce)
    return response.to_dictionary()


def parse_query_parameters():
    query: Any = request.query
    timestamp: str = query.timestamp
    block_nonce: int = query.blockNonce

    if timestamp and block_nonce:
        raise RequestError("only one of the following can be specified: 'timestamp', 'blockNonce'")

    try:
        timestamp_parsed = parse_time(timestamp) if timestamp else None
        block_nonce_parsed = int(block_nonce) if block_nonce else None
    except:
        raise RequestError("cannot parse query parameters: 'timestamp', 'blockNonce'")

    return timestamp_parsed, block_nonce_parsed


def parse_time(timestamp: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
