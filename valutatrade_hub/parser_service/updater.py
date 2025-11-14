import inspect

from requests import Response

from .config import ParserConfig
from .api_clients.abc import (BaseApiClient, RagesType, ApiRequestError,
                              ApiHTTPError)
from .models.storage import Storage
from datetime import datetime
from .log_record import HTTPLogRecord
from valutatrade_hub.logger import Logger
from valutatrade_hub.logging_config.log_record import LogRecord
import logging
from traceback import extract_tb
from .models import Rate


class UnknownRateError(Exception):
    def __init__(self, from_currency: str, to_currency: str):
        self._from_currency = from_currency
        self._to_currency = to_currency

    @property
    def from_currency(self) -> str:
        return self._from_currency

    @property
    def to_currency(self) -> str:
        return self._to_currency

    def __str__(self):
        return (f"Неизвестный курс "
                f"{self._from_currency} -> {self._to_currency}")


class RatesUpdater:
    """
    Класс для обновления данных о курсах валют.

    :param config: Конфигурация парсера.
    :api_clients: Клиенты для получения данных о курсах валют.
    """
    def __init__(
            self,
            config: ParserConfig,
            logger: Logger,
            *api_clients: BaseApiClient
    ):
        if any(
                not isinstance(client, BaseApiClient)
                for client in api_clients
        ):
            raise TypeError(
                "Все аргументы должны быть экземплярами класса BaseApiClient"
            )
        self._api_clients = api_clients
        self._storage: Storage | None = None
        self._config = config
        self._logger: logging.Logger = logger.logger()

    @property
    def storage(self) -> Storage:
        return self._storage

    def run_update(self):
        """
        Обновление данных.

        :return: None.

        :raises
            valutatrade_hub.parser_service.api_clients.abc.BaseApiClientError:
                Ошибка при запросе к API.
        """
        last_refresh = datetime.now()
        action = inspect.stack()[0].function
        pairs: RagesType = {}
        for client in self._api_clients:
            try:
                rates: RagesType = client.fetch_rates()
                pairs.update(rates)
            except ApiHTTPError as e:
                response: Response = e.response
                self._logger.error(
                    HTTPLogRecord(
                        action=action,
                        result="error",
                        error_type=e.__class__.__name__,
                        error_message=str(e),
                        url=response.url,
                        response_status_code=response.status_code,
                        response_text=response.text
                    )
                )
            except ApiRequestError as e:
                self._logger.error(
                    HTTPLogRecord(
                        action=action,
                        result="error",
                        error_type=e.error_type,
                        error_message=e.error,
                        message=str(e),
                        url=e.url
                    )
                )
            except Exception as e:
                tb = extract_tb(e.__traceback__)
                self._logger.error(
                    LogRecord(
                        action=action,
                        result="error",
                        error_type=e.__class__.__name__,
                        error_message=str(e),
                        message=str(tb)
                    )
                )
            else:
                self._logger.info(
                    LogRecord(
                        action=action,
                        result="success",
                        message=str(client.info)
                    )
                )
        self._storage = Storage(
            pairs=pairs,
            last_refresh=last_refresh
        )

    def _get_rate_from_storage(self, key: str) -> float | None:
        try:
            rate: Rate = self._storage.pairs[key]
            return rate.rate
        except KeyError:
            return None

    def _get_rate(self, from_currency: str, to_currency: str) -> Rate | None:
        """
        Получение курса валюты из хранилища.

        :param from_currency: код конвертируемой валюты.
        :param to_currency: код валюты, в которую конвертируется.
        :return: курс валюты, если он есть в хранилище, иначе None.
        """
        key: str = BaseApiClient.rate_key(from_currency, to_currency)
        return self._storage.pairs.get(key)

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Получение курса валюты.

        :param from_currency: код конвертируемой валюты.
        :param to_currency: код валюты, в которую конвертируется.
        :return: курс валюты.

        :raises UnknownRateError: если курс не найден.
        """
        rate: Rate = self._get_rate(from_currency, to_currency)
        if rate:
            return rate.rate

        rate = self._get_rate(to_currency, from_currency)
        if rate:
            return 1 / rate.rate

        raise UnknownRateError(from_currency, to_currency)
