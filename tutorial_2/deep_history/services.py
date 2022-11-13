from deep_history.network_provider import CustomNetworkProvider


class Services:
    def __init__(self, mainnet_url: str, devnet_url: str) -> None:
        self.mainnet_network_provider = CustomNetworkProvider(mainnet_url)
        self.devnet_network_provider = CustomNetworkProvider(devnet_url)

    def get_network_provider(self, network: str):
        if network == "mainnet":
            return self.mainnet_network_provider
        elif network == "devnet":
            return self.devnet_network_provider
        raise Exception(f"unknown network: {network}")
