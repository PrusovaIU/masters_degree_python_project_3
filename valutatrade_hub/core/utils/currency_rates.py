from requests import get, Response
import threading


RatesType = dict[str, float]


def get_exchange_rate(base_currency: str) -> RatesType:
    """
    Получить курсы валют.

    :param base_currency: код валюты, относительно которой будут получены
        курсы.

    :return: словарь с курсами валют вида {код валюты: курс}.

    :raises requests.exceptions.RequestException: если произошла ошибка
        при запросе к API.
    """
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response: Response = get(url)
    response.raise_for_status()
    data: dict = response.json()
    return data["rates"]
