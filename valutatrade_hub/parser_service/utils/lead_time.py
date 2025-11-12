from time import time
from typing import Optional


class LeadTime:
    """Контекстный менеджер для измерения времени выполнения блока кода"""
    def __init__(self):
        self._start: Optional[float] = None
        self._end: Optional[float] = None
        self._duration: Optional[int] = None

    @property
    def duration(self) -> Optional[int]:
        """
        :return: длительность выполнения блока кода в миллисекундах
        """
        return self._duration

    def __enter__(self) -> "LeadTime":
        self._start = time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end = time()
        self._duration = int(self._end - self._start) * 1000
        if exc_type:
            raise exc_val

