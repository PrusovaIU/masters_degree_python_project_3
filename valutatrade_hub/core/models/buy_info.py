from dataclasses import dataclass
from typing import Optional
from .wallet import Wallet


@dataclass
class BuyInfo:
    """
    Информация о покупке
    """
    #: сумма покупки
    amount: float
    #: валюта покупки
    currency: str
    #: базовая валюта
    base_currency: str
    #: курс базовая валюта/валюта покупки
    rate: Optional[float] = None
    #: баланс до покупки
    before_balance: Optional[float] = None
    #: баланс после покупки
    after_balance: Optional[float] = None
    #: кошелек
    wallet: Optional[Wallet] = None
