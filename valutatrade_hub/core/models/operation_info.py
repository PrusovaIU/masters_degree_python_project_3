from dataclasses import dataclass
from typing import Optional
from .wallet import Wallet


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
    #: валюта покупки
    currency: str
    #: базовая валюта
    base_currency: str
    #: тип операции
    operation_type: str
    #: курс базовая валюта/валюта покупки
    rate: Optional[float] = None
    #: баланс до покупки
    before_balance: Optional[float] = None
    #: баланс после покупки
    after_balance: Optional[float] = None
    #: кошелек
    wallet: Optional[Wallet] = None
