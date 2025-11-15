from requests import Response

from .config import ParserConfig
from .api_clients.abc import (BaseApiClient, ClientApiRequestError,
                              ApiHTTPError)
from .models.rate import RatesType
from .models import ExchangeRate
from .models.storage import Storage
from datetime import datetime
from .log_record import HTTPLogRecord
from valutatrade_hub.logger import Logger
from valutatrade_hub.logging_config.log_record import LogRecord
import logging
from traceback import extract_tb
from .models import Rate
from .utils.files import write_file
from .exception import ApiRequestError, UnknownRateError


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
        self._rates_file_path = config.data_path / "rates.json"
        self._exchanges_file_path = config.data_path / "exchanges_rates.json"
        self._logger: logging.Logger = logger.logger()

    @property
    def storage(self) -> Storage:
        return self._storage

    def run_update(self, source: str | None = None):
        """
        Обновление данных.

        :return: None.

        :raises
            valutatrade_hub.parser_service.api_clients.abc.BaseApiClientError:
                Ошибка при запросе к API.
        """
        last_refresh = datetime.now()
        pairs: RatesType = self._storage.pairs.copy() if self._storage else {}
        exchanges: list[ExchangeRate] = []
        if source:
            clients = [
                client for client in self._api_clients
                if client.__class__.__name__ == source
            ]
            if not clients:
                raise ValueError(f"Не найден клиент с именем {source}")
        else:
            clients = self._api_clients
        for client in clients:
            rates = self._client_fetch_rates(client)
            pairs.update(rates)
            exchanges.extend(client.history)
        self._storage = Storage(
            pairs=pairs,
            last_refresh=last_refresh
        )
        write_file(
            self._rates_file_path,
            self._storage.dump(),
            "write_rates_file"
        )
        write_file(
            self._exchanges_file_path,
            [record.dump() for record in exchanges],
            "write_exchanges_file"
        )

    def _client_fetch_rates(self, client: BaseApiClient) -> RatesType:
        """
        Вызов метода fetch_rates у клиента.

        :param client: клиент для получения данных о курсах валют.
        :return: курсы валют.
        """
        action = "fetch_rates"
        try:
            rates: RatesType = client.fetch_rates()
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
        except ClientApiRequestError as e:
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
            raise e
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
            raise ApiRequestError(e)
        else:
            self._logger.info(
                LogRecord(
                    action=action,
                    result="success",
                    message=str(client.info)
                )
            )
        return rates
