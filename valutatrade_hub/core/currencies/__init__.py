from .fiat import FiatCurrency
from .crypto import CryptoCurrency
from .abc import Currency

__all__ = [
    "FiatCurrency",
    "CryptoCurrency",
    "get_currency",
    "CurrencyNotFoundError"
]

# Реестр валют: код -> экземпляр Currency
_CURRENCY_REGISTRY: dict[str, Currency] = {
    "USD": FiatCurrency(
        "US Dollar", "USD", "United States"
    ),
    "EUR": FiatCurrency(
        "Euro", "EUR", "Eurozone"
    ),
    "GBP": FiatCurrency(
        "British Pound", "GBP", "United Kingdom"
    ),
    "RUB": FiatCurrency(
        "Russian Ruble", "RUB", "Russia"
    ),
    "BTC": CryptoCurrency(
        "Bitcoin", "BTC", "SHA-256", 1.12e12
    ),
    "ETH": CryptoCurrency(
        "Ethereum", "ETH", "Ethash", 4.5e11
    ),
    "SOL": CryptoCurrency(
        "Solana", "SOL", "SHA-256", 1e10
    ),
}


class CurrencyNotFoundError(Exception):
    """Исключение, выбрасываемое, если валюта с указанным кодом не найдена."""
    def __init__(self, currency_code: str):
        self._currency_code = currency_code

    def __str__(self):
        return f"Валюта с кодом \"{self._currency_code}\" не найдена."


def get_currency(code: str) -> Currency:
    """
    Фабричный метод: возвращает экземпляр валюты по коду.

    :param code: код валюты (например, "USD", "BTC").
    :return: объект Currency.

    :raises CurrencyNotFoundError: если валюта с таким кодом не
        зарегистрирована.
    """
    try:
        return _CURRENCY_REGISTRY[code]
    except KeyError as e:
        raise CurrencyNotFoundError(code)

