from abc import ABCMeta, abstractmethod
from re import match


class Currency(metaclass=ABCMeta):
    def __init__(self, name: str, code: str, *args, **kwargs):
        if not match(r"^[\w ]+$", name):
            raise ValueError(
                f"Некорректное название валюты. Название должно состоять из "
                f"латинских букв и цифр. Получено: {name}"
            )
        if not match(r"^[A-Z]{2,5}$", code):
            raise ValueError(
                f"Некорректный код валюты. Код должен состоять из 2-5 "
                f"заглавных букв. Получено: {code}"
            )
        self.name = name
        self.code = code

    @abstractmethod
    def get_display_info(self) -> str:
        """
        :return: строковое представление для UI/логов.
        """
        pass
