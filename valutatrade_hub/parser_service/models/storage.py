from datetime import datetime
from enum import Enum
from typing import NamedTuple

from ..exception import UnknownRateError
from .rate import Rate, RatesType, parse_rate_key, rate_key

RateDictType = dict[str, float]


class StorageJsonKey(Enum):
    pairs = "pairs"
    last_refresh = "last_refresh"


class Storage(NamedTuple):
    """
    Класс хранилища данных о курсах валют.
    """
    pairs: RatesType
    last_refresh: datetime

    def get_exchange_rate(self, currency: str) -> RateDictType:
        """
        Получение курсов валюты.

        :param currency: код валюты, относительно которой будут получены
            курсы.

        :return: словарь с курсами валют вида {код валюты: курс}.
        """
        rates: RateDictType = {}
        for key, value in self.pairs.items():
            fc, tc = parse_rate_key(key)
            if currency == fc:
                rates[tc] = value.rate
            elif currency == tc:
                rates[fc] = 1 / value.rate
        return rates

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Получение курса валюты.

        :param from_currency: код конвертируемой валюты.
        :param to_currency: код валюты, в которую конвертируется.
        :return: курс валюты.

        :raises valutatrade_hub.parser_service.exception.UnknownRateError:
            если курс не найден.
        """
        if from_currency == to_currency:
            return 1
        rate = self._get_rate(from_currency, to_currency)
        if rate:
            return rate
        rate = self._get_rate(to_currency, from_currency)
        if rate:
            return 1 / rate
        else:
            raise UnknownRateError(from_currency, to_currency)

    def _get_rate(self, from_currency: str, to_currency: str) -> float | None:
        """
        Получение курса валюты из внутреннего хранилища.
        :param from_currency: код конвертируемой валюты.
        :param to_currency: код валюты, в которую конвертируется.
        :return: курс валюты, если найден, иначе None.
        """
        key: str = rate_key(from_currency, to_currency)
        try:
            rate: Rate = self.pairs[key]
            return rate.rate
        except KeyError:
            return None

    def top(self, count: int) -> RateDictType:
        """
        Получение топа валют по курсу.

        :param count: количество валют в топе.
        :return: список валют с курсами.
        """
        rates = {}
        for key, value in self.pairs.items():
            if 1 > value.rate > 0:
                value = 1 / value.rate
                fc, tc = parse_rate_key(key)
                key = rate_key(tc, fc)
            else:
                value = value.rate
            rates[key] = value
        sorted_rates = sorted(
            rates.items(),
            key=lambda v: v[-1],
            reverse=True
        )
        return {
            key: value for key, value in sorted_rates[:count]
        }

    @classmethod
    def load(cls, data: dict) -> "Storage":
        pairs = {
            key: Rate(**value)
            for key, value in data[StorageJsonKey.pairs.value].items()
        }
        return cls(
            pairs=pairs,
            last_refresh=datetime.fromisoformat(
                data[StorageJsonKey.last_refresh.value]
            )
        )

    def dump(self) -> dict:
        return {
            StorageJsonKey.pairs.value: {
                key: value.dump() for key, value in self.pairs.items()
            },
            StorageJsonKey.last_refresh.value: self.last_refresh.isoformat()
        }

