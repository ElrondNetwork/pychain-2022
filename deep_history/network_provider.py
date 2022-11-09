import datetime
from functools import lru_cache
from typing import Any, Dict, List

from erdpy_network import ProxyNetworkProvider

MAX_NUM_BLOCKS_LOOKAHEAD = 64


class CustomNetworkProvider(ProxyNetworkProvider):
    def __init__(self, url: str) -> None:
        super().__init__(url)

    @lru_cache(maxsize=1024)
    def get_native_state_of_account(self, address: str, time: datetime.datetime):
        block = self.get_block_by_time(address, time)
        block_nonce = block.get("nonce")
        response = self.do_get(f"address/{address}?blockNonce={block_nonce}")
        return response

    @lru_cache(maxsize=1024)
    def get_token_state_of_account(self, address: str, token: str, time: datetime.datetime):
        block = self.get_block_by_time(address, time)
        block_nonce = block.get("nonce")
        response = self.do_get(f"address/{address}/esdt{token}?blockNonce={block_nonce}")
        return response

    @lru_cache(maxsize=64 * 1024)
    def get_block_by_time(self, address_of_interest: str, time: datetime.datetime):
        shard = self.get_shard_of_address(address_of_interest)
        round = self.get_round_by_time(time)

        for _ in range(0, MAX_NUM_BLOCKS_LOOKAHEAD):
            blocks: List[Dict[str, Any]] = self.get_blocks_of_by_round(shard, round)
            if blocks:
                first_block = blocks[0]
                return first_block

        raise Exception(f"Unexpected (rare) condition: no blocks at (or close after) ~{time}")

    @lru_cache(maxsize=64 * 1024)
    def get_shard_of_address(self, address: str) -> int:
        response = self.do_get(f"address/{address}/shard")
        shard = response.get("shardID")
        return shard

    @lru_cache(maxsize=64 * 1024)
    def get_blocks_of_by_round(self, shard: int, round: int) -> List[Dict[str, Any]]:
        response = self.do_get(f"blocks/by-round/{round}")
        blocks = response.get("blocks")
        blocks_of_shard = [block for block in blocks if block.get("shard") == shard]
        return blocks_of_shard

    @lru_cache(maxsize=64 * 1024)
    def get_round_by_time(self, time: datetime.datetime):
        genesis_time = self.get_genesis_time()
        delta = (time - genesis_time).total_seconds()
        round = int(delta / self.get_round_duration())
        return round

    @lru_cache
    def get_genesis_time(self):
        network_config = self.get_network_config()
        erd_start_time = network_config.get("erd_start_time")
        genesis_time = datetime.datetime.utcfromtimestamp(erd_start_time)
        return genesis_time

    @lru_cache
    def get_round_duration(self) -> float:
        network_config = self.get_network_config()
        erd_round_duration = network_config.get("erd_round_duration")
        return erd_round_duration / 1000

    @lru_cache
    def get_network_config(self):
        return self.do_get("network/config")
