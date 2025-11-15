class ApiRequestError(Exception):
    pass


class UnknownRateError(ApiRequestError):
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
