from .abc import BaseApiClient
from .exchange_rate import ExchangeRateApiClient
from .coin_gecko import CoinGeckoClient
from ..config import ParserConfig


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
