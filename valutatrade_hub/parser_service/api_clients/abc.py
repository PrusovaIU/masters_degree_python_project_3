from abc import ABCMeta, abstractmethod
import requests
from valutatrade_hub.parser_service import models


class BaseApiClientError(Exception):
    pass


class BACRequestError(BaseApiClientError):
    pass


RagesType = dict[str, models.Rate]


class BaseApiClient(metaclass=ABCMeta):
    def __init__(self, request_timeout: int, max_history_size: int):
        self._history: list[models.ExchangeRate] = []
        self._request_timeout = request_timeout
        self._max_history_size = max_history_size

    @abstractmethod
    def url(self) -> str:
        """
        :return: URL для обращения к API.
        """
        pass

    @abstractmethod
    def parse_response(
            self,
            response: requests.Response
    ) -> list[models.ExchangeRate]:
        """
        Парсинг ответа от API.

        :param response: ответ от API.
        :return: список курсов валют.
        """
        pass

    @staticmethod
    def _form_rages(
            exchange_rates: list[models.ExchangeRate]
    ) -> RagesType:
        rates = {}
        for item in exchange_rates:
            key = f"{item.from_currency}_{item.to_currency}"
            rates[key] = models.Rate(
                item.rate,
                item.timestamp,
                item.source
            )
        return rates

    def get_data(self) -> RagesType:
        """
        Получение данных от API.

        :return: словарь курсов валют виз {from_currency_to_currency: Rate}.

        :raises BACRequestError: ошибка при обращении к API.
        """
        try:
            response: requests.Response = requests.get(
                self.url(),
                timeout=self._request_timeout
            )
            data = self.parse_response(response)
            self._history.extend(data)
            if len(self._history) > self._max_history_size:
                self._history = self._history[-self._max_history_size:]
            return self._form_rages(data)
        except requests.RequestException as e:
            raise BACRequestError(f"{e} ({e.__class__.__name__})")

