from abc import ABCMeta, abstractmethod
from typing import Optional

import requests
from valutatrade_hub.parser_service import models
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.utils.lead_time import LeadTime



class BaseApiClientError(Exception):
    pass


class ApiRequestError(BaseApiClientError):
    pass


RagesType = dict[str, models.Rate]


class BaseApiClient(metaclass=ABCMeta):
    def __init__(self, config: ParserConfig):
        self._history: list[models.ExchangeRate] = []
        self._config = config

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

    @staticmethod
    def _form_rages(
            exchange_rates: list[models.ExchangeRate]
    ) -> RagesType:
        """
        Формирование словаря курсов валют.

        :param exchange_rates: список журнальных записей.
        :return: словарь курсов валют виз {from_currency_to_currency: Rate}.
        """
        rates = {}
        for item in exchange_rates:
            key = f"{item.from_currency}_{item.to_currency}"
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
        except requests.RequestException as e:
            raise ApiRequestError(
                f"Не удалось получить данные от \"{e.request.url}\": {e} "
                f"({e.__class__.__name__})"
            )
