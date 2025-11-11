from requests import get, Response
from requests.exceptions import HTTPError, RequestException
from valutatrade_hub.core.exceptions import CoreError


class CurrencyRatesError(CoreError):
    pass


class UnknownCurrencyError(CurrencyRatesError):
    def __init__(self, currency: str):
        self._currency = currency

    def __str__(self):
        return f"Неизвестная валюта: {self._currency}"


RatesType = dict[str, float]


def get_exchange_rate(base_currency: str) -> RatesType:
    """
    Получить курсы валют.

    :param base_currency: код валюты, относительно которой будут получены
        курсы.

    :return: словарь с курсами валют вида {код валюты: курс}.

    :raises CurrencyRatesError: при ошибке получения данных.
    """
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    try:
        response: Response = get(url, timeout=10)
        response.raise_for_status()
        data: dict = response.json()
        return data["rates"]
    except HTTPError as e:
        if e.response.status_code == 404:
            raise UnknownCurrencyError(base_currency)
        else:
            raise CurrencyRatesError(f"Не удалось получить курс валют: {e}")
    except RequestException as e:
        raise CurrencyRatesError(f"Не удалось получить курс валют: {e}")


def get_rate(from_currency: str, to_currency: str) -> float:
    """
    Получение курса валюты.

    :param from_currency: код валюты, из которой конвертируется.
    :param to_currency: код валюты, в которую конвертируется.
    :return: курс валюты.

    :raises CurrencyRatesError: если не удалось получить курс валюты.
    """
    try:
        rates: RatesType = get_exchange_rate(from_currency)
        return rates[to_currency]
    except KeyError as e:
        raise UnknownCurrencyError(str(e))
