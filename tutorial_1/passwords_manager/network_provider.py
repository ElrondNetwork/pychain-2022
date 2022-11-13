import datetime
import time
from functools import lru_cache
from typing import Any, Dict, List, Union

from erdpy_network import ProxyNetworkProvider


class CustomNetworkProvider(ProxyNetworkProvider):
    def __init__(self, url: str) -> None:
        super().__init__(url)

    @lru_cache()
    def get_network_config(self):
        return self.do_get("network/config").get("config")

    def do_get(self, url: str):
        start = time.time()
        response = super().do_get(url)
        end = time.time()
        print(f"> GET {url}, duration = {end - start}")
        return response
