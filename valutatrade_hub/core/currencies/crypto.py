from re import match

from .abc import Currency


class CryptoCurrency(Currency):
    """
    Класс для криптовалют.

    :param name: Название криптовалюты
    :param code: Код криптовалюты.
    :param algorithm: Алгоритм хеширования.
    :market_cap: Рыночная капитализация криптовалюты.
    """

    def __init__(
            self,
            name: str,
            code: str,
            algorithm: str,
            market_cap: float
    ):
        super().__init__(name, code)
        if not match(r"[\w-]+", algorithm):
            raise ValueError(
                "Алгоритм хеширования должен быть непустой строкой."
            )
        if market_cap < 0:
            raise ValueError(
                "Рыночная капитализация не может быть отрицательной."
            )

        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        mcap_str = f"{self.market_cap:.2e}"  # Формат: 1.12e12
        return (f"[CRYPTO] {self.code} — {self.name} "
                f"(Algo: {self.algorithm}, MCAP: {mcap_str})")
