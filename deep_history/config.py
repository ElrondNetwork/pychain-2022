from typing import Any, Dict


class Environment:
    def __init__(self, network_provider_url: str) -> None:
        self.network_provider_url = network_provider_url


ENVIRONMENTS: Dict[str, Any] = {
    "devnet": Environment("http://r620:9090"),
    "mainnet": Environment("http://r620:8080"),
}
