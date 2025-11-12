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
        if not match(r"^\w+$", issuing_country):
            raise ValueError(
                "Страна эмиссии не должна быть пустой строкой и "
                "должна состоять только из букв английского алфавита."
            )
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return (f"[FIAT] {self.code} — {self.name} "
                f"(Issuing: {self.issuing_country})")
