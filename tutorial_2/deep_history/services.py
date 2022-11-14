from deep_history.network_provider import CustomNetworkProvider


class Services:
    def __init__(self, mainnet_provider: CustomNetworkProvider, devnet_provider: CustomNetworkProvider) -> None:
        self.mainnet_network_provider = mainnet_provider
        self.devnet_network_provider = devnet_provider

    def get_network_provider(self, network: str):
        if network == "mainnet":
            return self.mainnet_network_provider
        elif network == "devnet":
            return self.devnet_network_provider
        raise Exception(f"unknown network: {network}")
