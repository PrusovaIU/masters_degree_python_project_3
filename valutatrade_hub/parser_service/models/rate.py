from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RateJsonKey(Enum):
    rate = "rate"
    updated_at = "updated_at"
    source = "source"


@dataclass
class Rate:
    """
    Информация о курсе валюты
    """
    rate: float
    updated_at: datetime
    source: str

    def dump(self) -> dict:
        return {
            RateJsonKey.rate.value: self.rate,
            RateJsonKey.updated_at.value: self.updated_at.isoformat(),
            RateJsonKey.source.value: self.source
        }


RatesType = dict[str, Rate]  # {from_currency_to_currency: Rate}


def rate_key(from_currency: str, to_currency: str) -> str:
    """
    Формирование ключа для хранения курса валюты.

    :param from_currency: конвертируемая валюта.
    :param to_currency: валюта, в которую производится конвертация.
    :return: ключ для хранения курса валюты.
    """
    return f"{from_currency}_{to_currency}"


def parse_rate_key(key: str) -> tuple[str, str]:
    """
    Парсинг ключа для хранения курса валюты.

    :param key: ключ.
    :return: конвертируемая и валюта, в которую производится конвертация.
    """
    fc, tc = key.split("_")
    return fc, tc
