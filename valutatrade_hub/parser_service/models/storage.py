from enum import Enum

from ..api_clients.abc import RagesType
from typing import NamedTuple
from datetime import datetime


class StorageJsonKey(Enum):
    pairs = "pairs"
    last_refresh = "last_refresh"


class Storage(NamedTuple):
    """
    Класс хранилища данных о курсах валют.
    """
    pairs: RagesType
    last_refresh: datetime

    # @classmethod
    # def load(cls, data: dict) -> "Storage":
    #     return cls(
    #         pairs=data[StorageJsonKey.pairs.value],
    #         last_refresh=datetime.fromisoformat(
    #             data[StorageJsonKey.last_refresh.value]
    #         )
    #     )

    def dump(self) -> dict:
        return {
            StorageJsonKey.pairs.value: {
                key: value.dump() for key, value in self.pairs.items()
            },
            StorageJsonKey.last_refresh.value: self.last_refresh.isoformat()
        }

