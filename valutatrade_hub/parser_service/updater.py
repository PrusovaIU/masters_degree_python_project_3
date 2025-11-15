from pathlib import Path

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
        self._log_dir_path: Path = logger.logs_dir_path

        self._console_logger: logging.Logger = logging.getLogger("updater")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        self._console_logger.addHandler(console_handler)

    @property
    def storage(self) -> Storage:
        return self._storage

    def run_update(self, source: str | None = None):
        """
        Обновление данных.

        :return: None.
        """
        self._console_logger.info("Starting rates update...")
        last_refresh = datetime.now()
        pairs, exchanges, errors = self._call_clients(source)
        self._storage = Storage(
            pairs=pairs,
            last_refresh=last_refresh
        )
        self._write_files(exchanges)
        if errors:
            log = (f"Update completed with errors. "
                   f"Check {self._log_dir_path.absolute()} for details. ")
        else:
            log = (f"Update successful. Total rates updated: {len(pairs)}. "
                   f"Last refresh: {last_refresh.isoformat()}")
        self._console_logger.info(log)

    def _call_clients(
            self,
            source: str | None
    ) -> tuple[RatesType, list[ExchangeRate], int]:
        errors = 0
        pairs: RatesType = self._storage.pairs.copy() if self._storage else {}
        exchanges: list[ExchangeRate] = []
        for client in self._filter_clients(source):
            try:
                rates = self._client_fetch_rates(client)
            except Exception as e:
                self._console_logger.error(
                    f"Failed to fetch from {client.info.name}: {e}"
                )
                errors += 1
            else:
                pairs.update(rates)
                exchanges.extend(client.history)
                self._console_logger.info(
                    f"Fetching from {client.info.name}... OK "
                    f"({len(rates)} rates)"
                )
        return pairs, exchanges, errors

    def _filter_clients(self, source: str) -> list[BaseApiClient]:
        """
        Фильтрация клиентов по имени.

        :param source: имя клиента.
        :return: список клиентов.
        """
        if source:
            clients = [
                client for client in self._api_clients
                if client.__class__.__name__ == source
            ]
            if not clients:
                raise ValueError(f"Не найден клиент с именем {source}")
        else:
            clients = self._api_clients
        return clients

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
            raise e
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
            raise e
        else:
            self._logger.info(
                LogRecord(
                    action=action,
                    result="success",
                    message=client.info._asdict()
                )
            )
        return rates

    def _write_files(self, exchanges: list[ExchangeRate]) -> None:
        """
        Запись данных в файлы.

        :param exchanges: список журнальных записей.
        :return: None.
        """
        write_file(
            self._rates_file_path,
            self._storage.dump(),
            "write_rates_file"
        )
        self._console_logger.info(
            f"Writing {len(self._storage.pairs)} rates to "
            f"{self._rates_file_path.absolute()}..."
        )
        write_file(
            self._exchanges_file_path,
            [record.dump() for record in exchanges],
            "write_exchanges_file"
        )
