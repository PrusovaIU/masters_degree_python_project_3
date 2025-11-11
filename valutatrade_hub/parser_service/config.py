from typing import Optional

from dotenv import load_dotenv
from pathlib import Path
from os import environ


class ConfigError(Exception):
    pass


class ParserConfig:
    def __init__(self):
        self.coingecko_url: str = \
            "https://api.coingecko.com/api/v3/simple/price"
        self.exchangerate_api_url: str = \
            "https://v6.exchangerate-api.com/v6"
        self.exchangerate_api_key: Optional[str] = None

        # Списки валют
        self.base_currency: str = "USD"
        self.fiat_currencies: tuple[str, ...] = ("EUR", "GBP", "RUB")
        self.crypto_currencies: tuple[str, ...] = ("BTC", "ETH", "SOL")
        self.crypto_id_map: dict[str, str] = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
        }

        # Пути
        self.rates_file_path: str = "data/rates.json"
        self.history_file_path: str = "data/exchange_rates.json"

        # Сетевые параметры
        self.request_timeout: int = 10

    def load(self, file_path: Path) -> None:
        """
        Загрузка конфигурации из файла .env.

        :param file_path: путь к файлу .env
        :return: None.

        :raises ConfigError: если не удалосьзагрузить конфигурацию.
        """
        try:
            load_dotenv(file_path)
            self.exchangerate_api_key = environ["EXCHANGERATE_API_KEY"]
            self.base_currency = environ.get(
                "BASE_CURRENCY", self.base_currency
            )
            self.rates_file_path = environ.get(
                "RATES_FILE_PATH", self.rates_file_path
            )
            self.history_file_path = environ.get(
                "HISTORY_FILE_PATH", self.history_file_path
            )
            self.request_timeout = int(
                environ.get("REQUEST_TIMEOUT", self.request_timeout)
            )
        except KeyError as e:
            raise ConfigError(f"Не найден ключ {e}")
        except OSError as e:
            raise ConfigError(f"Ошибка чтения файла {file_path}: {e}")



