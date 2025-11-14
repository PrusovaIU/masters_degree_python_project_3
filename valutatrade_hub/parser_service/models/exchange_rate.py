from dataclasses import dataclass, field
from datetime import datetime
from http import HTTPStatus
from enum import Enum

@dataclass
class ExchangeRateMeta:
    raw_id: str
    request_ms: int
    status_code: HTTPStatus
    etag: str = field(default="W/\"abc123\"")


class SimpleExchangeRateJsonKeys(Enum):
    id = "id"
    from_currency = "from_currency"
    to_currency = "to_currency"
    rate = "rate"
    source = "source"


class ExchangeRateJsonKeys(Enum):
    timestamp = "timestamp"
    meta = "meta"


@dataclass
class ExchangeRate:
    """
    Запись о курсе валюты для журнала измерений
    """
    id: str = field(init=False)
    from_currency: str
    to_currency: str
    rate: float
    timestamp: datetime
    timestamp_iso: str = field(init=False)
    source: str
    meta: ExchangeRateMeta

    def __post_init__(self):
        self.timestamp_iso = self.timestamp.isoformat()
        self.id = \
            f"{self.from_currency}_{self.to_currency}_{self.timestamp_iso}"

    @classmethod
    def load(cls, data: dict) -> "ExchangeRate":
        """
        Создание нового экземпляра класса из словаря.

        :param data: параметры экземпляра класса.
        :return: новый экземпляр класса.

        :raises KeyError: если ключ не найден.
        """
        data.pop(SimpleExchangeRateJsonKeys.id.value)
        data[ExchangeRateJsonKeys.timestamp.value] = datetime.fromisoformat(
            data[ExchangeRateJsonKeys.timestamp.value]
        )
        data[ExchangeRateJsonKeys.meta.value] = ExchangeRateMeta(
            **data[ExchangeRateJsonKeys.meta.value]
        )
        return cls(**data)


    def dump(self) -> dict:
        """
        Сериализация в словарь.

        :return: словарь с параметрами экземпляра класса.
        """
        return {
            penum.value: getattr(self, penum.value)
            for penum in SimpleExchangeRateJsonKeys
        } | {
            ExchangeRateJsonKeys.timestamp.value: self.timestamp.isoformat(),
            ExchangeRateJsonKeys.meta.value: self.meta.__dict__
        }


# if __name__ == '__main__':
#     a = ExchangeRates(
#             from_currency="USD",
#             to_currency="RUB",
#             rate=75.0,
#             timestamp=datetime.now(),
#             source="https://www.cbr-xml-daily.ru/daily_json.js",
#             meta=ExchangeRateMeta(
#                     raw_id="USD_RUB",
#                     request_ms=100,
#                     status_code=HTTPStatus.OK,
#                     etag="1234567890"
#             )
#     )
#     aa = ExchangeRates.load(a.dump())
#     print(aa.dump())

