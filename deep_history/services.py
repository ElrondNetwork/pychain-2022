from deep_history.config import ENVIRONMENTS, Environment
from deep_history.network_provider import CustomNetworkProvider


class Services:
    def __init__(self) -> None:
        pass

    def get_network_provider(self, network: str):
        environment = self.get_environment(network)
        network_provider = CustomNetworkProvider(environment.network_provider_url)
        return network_provider

    def get_environment(self, network: str) -> Environment:
        return ENVIRONMENTS[network]
