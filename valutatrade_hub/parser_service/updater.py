from .config import ParserConfig
from .api_clients.abc import BaseApiClient, RagesType
from .models.storage import Storage
from datetime import datetime


class RatesUpdater:
    def __init__(self, config: ParserConfig, *api_clients: BaseApiClient):
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
        pairs: RagesType = {}
        for client in self._api_clients:
            rates: RagesType = client.fetch_rates()
            pairs.update(rates)
        self._storage = Storage(
            pairs=pairs,
            last_refresh=last_refresh
        )

