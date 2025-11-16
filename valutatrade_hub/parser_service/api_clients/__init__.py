from ..config import ParserConfig
from .abc import BaseApiClient
from .coin_gecko import CoinGeckoClient
from .exchange_rate import ExchangeRateApiClient

__all__ = [
    "BaseApiClient",
    "ExchangeRateApiClient",
    "CoinGeckoClient",
    "init_clients"
]


def init_clients(config: ParserConfig) -> list[BaseApiClient]:
    """
    Инициализация клиентов.

    :param config: конфигурация.
    :return: список клиентов.
    """
    return [
        ExchangeRateApiClient(config),
        CoinGeckoClient(config)
    ]
