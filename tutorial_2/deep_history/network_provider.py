import datetime
import time
from functools import lru_cache
from typing import Any, Dict, Union

from erdpy_network import ProxyNetworkProvider
from erdpy_network.network_config import NetworkConfig
from erdpy_network.resources import GenericResponse
from requests.auth import HTTPBasicAuth

MAX_NUM_BLOCKS_LOOKAHEAD = 64


class CustomNetworkProvider(ProxyNetworkProvider):
    def __init__(self, url: str, username: Union[str, None] = None, password: Union[str, None] = None) -> None:
        super().__init__(url, auth=HTTPBasicAuth(username, password))

    @lru_cache(maxsize=1024)
    def get_native_balance(self, address: str, time: Union[datetime.datetime, None], block_nonce: Union[int, None]):
        block_nonce = self.decide_block_nonce(address, time, block_nonce)
        block_nonce_query_part = "" if not block_nonce else f"blockNonce={block_nonce}"
        url = f"address/{address}?{block_nonce_query_part}"
        response = self.do_get_generic(url)
        return response

    @lru_cache(maxsize=1024)
    def get_token_balance(self, address: str, token: str, time: Union[datetime.datetime, None], block_nonce: Union[int, None]):
        block_nonce = self.decide_block_nonce(address, time, block_nonce)
        block_nonce_query_part = "" if not block_nonce else f"blockNonce={block_nonce}"
        response = self.do_get_generic(f"address/{address}/esdt/{token}?{block_nonce_query_part}")
        return response

    @lru_cache(maxsize=1024)
    def get_whole_storage(self, address: str, time: Union[datetime.datetime, None], block_nonce: Union[int, None]):
        block_nonce = self.decide_block_nonce(address, time, block_nonce)
        block_nonce_query_part = "" if not block_nonce else f"blockNonce={block_nonce}"
        response = self.do_get_generic(f"address/{address}/keys?{block_nonce_query_part}")
        return response

    @lru_cache(maxsize=1024)
    def get_storage_entry(self, address: str, key: str, time: Union[datetime.datetime, None], block_nonce: Union[int, None]):
        block_nonce = self.decide_block_nonce(address, time, block_nonce)
        block_nonce_query_part = "" if not block_nonce else f"blockNonce={block_nonce}"
        response = self.do_get_generic(f"address/{address}/key/{key}?{block_nonce_query_part}")
        return response

    def decide_block_nonce(self, address: str, time: Union[datetime.datetime, None], block_nonce: Union[int, None]):
        if time:
            block = self.get_block_by_time(address, time)
            block_nonce = block.get("nonce")

        return block_nonce

    @lru_cache(maxsize=64 * 1024)
    def get_block_by_time(self, address_of_interest: str, time: datetime.datetime):
        shard = self.get_shard_of_address(address_of_interest)
        round = self.get_round_by_time(time)

        for _ in range(0, MAX_NUM_BLOCKS_LOOKAHEAD):
            block = self.get_block_of_shard_by_round(shard, round)
            if block:
                return block

        raise Exception(f"Unexpected (rare) condition: no blocks at (or close after) ~{time}")

    @lru_cache(maxsize=64 * 1024)
    def get_shard_of_address(self, address: str) -> int:
        response = self.do_get_generic(f"address/{address}/shard")
        shard = response.get("shardID")
        return shard

    @lru_cache(maxsize=64 * 1024)
    def get_block_of_shard_by_round(self, shard: int, round: int) -> Union[Dict[str, Any], None]:
        # TODO: We should only cache responses if round < current round - (an arbitrary delta).
        response = self.do_get_generic(f"blocks/by-round/{round}")
        blocks = response.get("blocks")
        return next((block for block in blocks if block.get("shard") == shard), None)

    @lru_cache(maxsize=64 * 1024)
    def get_round_by_time(self, time: datetime.datetime):
        genesis_time = self.get_genesis_time()
        delta = (time - genesis_time).total_seconds()
        round = int(delta / self.get_round_duration())
        return round

    @lru_cache()
    def get_genesis_time(self):
        genesis_timestamp = self.cached_get_network_config().start_time
        genesis_time = datetime.datetime.utcfromtimestamp(genesis_timestamp)
        return genesis_time

    @lru_cache()
    def get_round_duration(self) -> float:
        round_duration = self.cached_get_network_config().round_duration
        return round_duration / 1000

    @lru_cache()
    def cached_get_network_config(self) -> NetworkConfig:
        return self.get_network_config()

    def do_get_generic(self, resource_url: str) -> GenericResponse:
        start = time.time()
        response = super().do_get_generic(resource_url)
        end = time.time()
        print(f"> GET {resource_url}, duration = {end - start}")
        return response
