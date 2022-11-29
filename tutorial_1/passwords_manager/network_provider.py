from functools import lru_cache
from typing import Any, Dict, List, Protocol

from erdpy_network import ProxyNetworkProvider

from passwords_manager.account_key_value import AccountKeyValue


class IAddress(Protocol):
    def bech32(self) -> str:
        return ""


class ITransaction(Protocol):
    def to_dictionary(self) -> Dict[str, Any]:
        return dict()


class CustomNetworkProvider(ProxyNetworkProvider):
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def get_account_nonce(self, address: IAddress) -> int:
        response = self.do_get_generic(f"address/{address.bech32()}")
        nonce = response.get("account").get("nonce", 0)
        return int(nonce)

    def get_storage(self, address: IAddress) -> List[AccountKeyValue]:
        response = self.do_get_generic(f"address/{address.bech32()}/keys")
        pairs_raw: Dict[str, str] = response.get("pairs")
        pairs: List[AccountKeyValue] = []

        for key, value in pairs_raw.items():
            key_bytes = bytes.fromhex(key)
            value_bytes = bytes.fromhex(value)
            pairs.append(AccountKeyValue(key_bytes, value_bytes))

        return pairs

    @lru_cache()
    def get_chain_id(self) -> str:
        return self.get_network_config().chain_id
