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
        response = self.do_get(f"address/{address.bech32()}")
        nonce = response.get("account").get("nonce", 0)
        return int(nonce)

    def send_transaction(self, transaction: ITransaction) -> str:
        payload = transaction.to_dictionary()
        response = self.do_post("transaction/send", payload)
        tx_hash = str(response.get("txHash"))
        return tx_hash

    def get_storage(self, address: IAddress) -> List[AccountKeyValue]:
        response = self.do_get(f"address/{address.bech32()}/keys")
        pairs_raw: Dict[str, str] = response.get("pairs")
        pairs: List[AccountKeyValue] = []

        for key, value in pairs_raw.items():
            key_bytes = bytes.fromhex(key)
            value_bytes = bytes.fromhex(value)
            pairs.append(AccountKeyValue(key_bytes, value_bytes))

        return pairs

    @lru_cache()
    def get_chain_id(self):
        return self.get_network_config().get("erd_chain_id")

    @lru_cache()
    def get_network_config(self):
        return self.do_get("network/config").get("config")
