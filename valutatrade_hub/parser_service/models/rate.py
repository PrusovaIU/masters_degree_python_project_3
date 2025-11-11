from dataclasses import dataclass
from datetime import datetime


@dataclass
class Rate:
    """
    Информация о курсе валюты
    """
    rate: float
    updated_at: datetime
    source: str
