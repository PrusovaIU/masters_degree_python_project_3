from dataclasses import dataclass, InitVar
from typing import Optional
from .wallet import Wallet
from ..currencies import get_currency, Currency


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
    operation_type: str
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
        self.currency = get_currency(self.currency_code)
