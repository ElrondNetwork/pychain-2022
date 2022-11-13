from functools import lru_cache

from erdpy_core import Address, Transaction
from erdpy_network import ProxyNetworkProvider


class CustomNetworkProvider(ProxyNetworkProvider):
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def get_account_nonce(self, address: Address) -> int:
        response = self.do_get(f"address/{address.bech32()}")
        nonce = response.get("account").get("nonce", 0)
        return int(nonce)

    def send_transaction(self, transaction: Transaction) -> str:
        payload = transaction.to_dictionary()
        response = self.do_post("transaction/send", payload)
        tx_hash = str(response.get("txHash"))
        return tx_hash

    def get_storage(self, address: Address):
        response = self.do_get(f"address/{address.bech32()}/keys")
        return response

    @lru_cache()
    def get_network_config(self):
        return self.do_get("network/config").get("config")
