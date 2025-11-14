from .abc import Currency
from re import match


class FiatCurrency(Currency):
    """
    Класс для фиатных валют.

    :param name: Название валюты.
    :param code: Код валюты.
    :param issuing_country: Страна эмиссии.
    """

    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        if not match(r"^[\w ]+$", issuing_country):
            raise ValueError(
                f"Страна эмиссии не должна быть пустой строкой и "
                f"должна состоять только из букв английского алфавита. "
                f"Введено: \"{issuing_country}\" для валюты {self.code}"
            )
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return (f"[FIAT] {self.code} — {self.name} "
                f"(Issuing: {self.issuing_country})")
