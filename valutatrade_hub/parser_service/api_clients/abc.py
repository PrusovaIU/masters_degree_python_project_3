from abc import ABCMeta, abstractmethod
from typing import Optional

import requests
from valutatrade_hub.parser_service import models
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.models.rate import RagesType, rate_key
from valutatrade_hub.parser_service.utils.lead_time import LeadTime
from valutatrade_hub.parser_service.exception import ApiRequestError


class ApiHTTPError(ApiRequestError):
    def __init__(self, response: requests.Response):
        self._response = response

    @property
    def response(self) -> requests.Response:
        return self._response

    def __str__(self):
        return (f"Ошибка при обращении к API: {self._response.text} "
                f"(status: {self._response.status_code})")


class ClientApiRequestError(ApiRequestError):
    def __init__(self, url: str, error_type: str, error: str | Exception):
        self._url = url
        self._error_type = error_type
        self._error = str(error)

    @property
    def url(self) -> str:
        return self._url

    @property
    def error_type(self) -> str:
        return self._error_type

    @property
    def error(self) -> str:
        return self._error

    def __str__(self):
        return (f"Ошибка при обращении к API \"{self._url}\": "
                f"{self._error} ({self._error_type})")


class BaseApiClient(metaclass=ABCMeta):
    def __init__(self, config: ParserConfig):
        self._history: list[models.ExchangeRate] = []
        self._config = config

    @property
    def history(self) -> list[models.ExchangeRate]:
        return self._history

    @property
    @abstractmethod
    def info(self) -> dict[str, str]:
        pass

    @abstractmethod
    def _call_api(self) -> list[models.ExchangeRate]:
        """
        Запрос к API.

        :return: список журнальных записей.
        """
        pass

    def _request(
            self,
            url: str,
            method: str = "GET",
            headers: Optional[dict] = None,
            params: Optional[dict] = None,
            json: Optional[dict] = None
    ) -> tuple[requests.Response, int]:
        """
         Запрос к API.

        :param url: url запроса.
        :param method: метод запроса (GET, POST, ...).
        :param headers: список заголовков.
        :param params: параметры запроса.
        :param json: json тела запроса.
        :return: ответ от API, время выполнения запроса.

        :raises requests.RequestException: ошибка при обращении к API.
        """
        with LeadTime() as lead_time:
            response: requests.Response = requests.request(
                method,
                url,
                params=params,
                data=json,
                headers=headers,
                timeout=self._config.request_timeout
            )
        response.raise_for_status()
        return response, lead_time.duration

    def _form_rages(
            self,
            exchange_rates: list[models.ExchangeRate]
    ) -> RagesType:
        """
        Формирование словаря курсов валют.

        :param exchange_rates: список журнальных записей.
        :return: словарь курсов валют виз {from_currency_to_currency: Rate}.
        """
        rates = {}
        for item in exchange_rates:
            key = rate_key(item.from_currency, item.to_currency)
            rates[key] = models.Rate(
                item.rate,
                item.timestamp,
                item.source
            )
        return rates

    def fetch_rates(self) -> RagesType:
        """
        Получение данных от API.

        :return: словарь курсов валют виз {from_currency_to_currency: Rate}.

        :raises BACRequestError: ошибка при обращении к API.
        """
        try:
            data = self._call_api()
            self._history.extend(data)
            if len(self._history) > self._config.max_history_len:
                self._history = self._history[-self._config.max_history_len:]
            return self._form_rages(data)
        except requests.HTTPError as e:
            raise ApiHTTPError(e.response)
        except requests.RequestException as e:
            raise ClientApiRequestError(e.request.url, e.__class__.__name__, e)
