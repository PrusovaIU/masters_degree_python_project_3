import inspect

from requests import Response

from .config import ParserConfig
from .api_clients.abc import (BaseApiClient, RagesType, ApiRequestError,
                              ApiHTTPError)
from .models.storage import Storage
from datetime import datetime
from .logger import Logger, HTTPLogRecord
from valutatrade_hub.logging_config.log_record import LogRecord
import logging
from traceback import extract_tb


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

