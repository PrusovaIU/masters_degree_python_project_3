class CoreError(Exception):
    pass


class CurrencyNotFoundError(CoreError):
    """Исключение, выбрасываемое, если валюта с указанным кодом не найдена."""
    def __init__(self, currency_code: str):
        self._currency_code = currency_code

    def __str__(self):
        return f"Неизвестная валюта \"{self._currency_code}\""


class InsufficientFundsError(CoreError):
    """
    Исключение, выбрасываемое, если на счету недостаточно средств для
    совершения операции.
    """
    def __init__(self, available: float, required: float, currency_code: str):
        self._available = available
        self._required = required
        self._currency_code = currency_code

    def __str__(self):
        return (f"Недостаточно средств: "
                f"доступно {self._available} {self._currency_code}, "
                f"требуется {self._required} {self._currency_code}")

# не стала реализовывать ApiRequestError в этом модуле, т.к. по заданию это
# исключение относится к ParserService. ApiRequestError реализовано в
# parser_service.api_clients.abc
