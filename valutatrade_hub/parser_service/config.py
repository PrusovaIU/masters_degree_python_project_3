from pathlib import Path

from valutatrade_hub.infra import JsonSettingsLoader, Parameter


class ConfigError(Exception):
    pass


class ParserConfig(JsonSettingsLoader):
    coingecko_url: str = Parameter(
        default="https://api.coingecko.com/api/v3/simple/price"
    )
    exchangerate_api_url: str = Parameter(
        default="https://v6.exchangerate-api.com/v6"
    )
    exchangerate_api_key: str = Parameter()
    base_currency: str = Parameter(default="USD")
    fiat_currencies: tuple = Parameter(default=("EUR", "GBP", "RUB"))
    crypto_currencies: dict = Parameter(
        ptype=dict,
        default={
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "solana": "SOL"
        }
    )
    rates_file_path: str = Parameter(default="data/rates.json")
    history_file_path: str = Parameter(default="data/exchange_rates.json")
    request_timeout: int = Parameter(ptype=int, default=10)
    max_history_len: int = Parameter(ptype=int, default=100)
    data_path: Path = Parameter(ptype=Path)
