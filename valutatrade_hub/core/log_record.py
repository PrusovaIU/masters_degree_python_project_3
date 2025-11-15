from dataclasses import dataclass

from valutatrade_hub.logging_config.log_record import LogRecord


@dataclass
class BalanceLogRecord(LogRecord):
    """Запись лога для операций с балансом."""
    #: имя пользователя:
    username: str = ""
    #: id пользователя:
    user_id: int = -1
    #: код валюты, в которой проводится операция:
    currency_code: str | None = None
    #: сумма операции (для операций с балансом):
    amount: float | None = None
    #: курс для валюты, в которой проводится операция относительно базовой
    #: валюты:
    rate: float | None = None
    #: базовая валюта:
    base: str | None = None

    def __str__(self):
        if self.error_type:
            return (f"{self.action} user='{self.username}' "
                    f"error='{self.error_type}' {self.error_message}")
        else:
            amount = format(self.amount, ',.4f') if self.amount else None
            rate = format(self.rate, ',.4f') if self.rate else None
            return (f"{self.action} user='{self.username}' "
                    f"currency='{self.currency_code}' "
                    f"amount='{amount}' "
                    f"rate='{rate}' "
                    f"base='{self.base}' "
                    f"result='{self.result}'")
