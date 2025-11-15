from dataclasses import dataclass, InitVar
from enum import Enum
from typing import Optional
from .wallet import Wallet
from ..currencies import get_currency, Currency


class BalanceOperationType(Enum):
    buy = "покупка"
    sell = "продажа"


@dataclass
class OperationInfo:
    """
    Информация о покупке
    """
    #: имя пользователя
    username: str
    #: id пользователя
    user_id: int
    #: сумма покупки
    amount: float
    #: код валюты покупки
    currency_code: str
    #: базовая валюта
    base_currency: str
    #: тип операции
    operation_type: BalanceOperationType
    #: валюта покупки
    currency: Currency | None = None
    #: курс базовая валюта/валюта покупки
    rate: Optional[float] = None
    #: баланс до покупки
    before_balance: Optional[float] = None
    #: баланс после покупки
    after_balance: Optional[float] = None
    #: кошелек
    wallet: Optional[Wallet] = None

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError(
                "Значение параметра \"amount\" должно быть больше нуля"
            )
        if self.operation_type == BalanceOperationType.sell:
            self.amount *= -1
        self.currency = get_currency(self.currency_code)
