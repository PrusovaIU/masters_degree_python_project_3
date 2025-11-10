from typing import Optional

from .wallet import Wallet
from valutatrade_hub.core.utils.currency_rates import get_exchange_rate
from enum import Enum


class ProtfolioJsonKeys(Enum):
    user = "user"
    wallets = "wallets"


class Portfolio:
    def __init__(self, user: int, wallets: dict[str, Wallet] = None):
        """
        Портфель пользователя.

        :param user: id пользователя.

        :param wallets: словарь с кошельками пользователя вида
            {код валюты: Wallet}
        """
        self._user = user
        self._wallets = wallets if wallets is not None else {}

    @property
    def user(self) -> int:
        return self._user

    @property
    def wallets(self) -> dict[str, Wallet]:
        return self._wallets

    def add_currency(self, currency_code: str) -> None:
        """
        Добавляет кошелек для указанной валюты.

        :param currency_code: код валюты.
        :return: кошелек для указанной валюты.
        """
        if currency_code in self._wallets:
            raise ValueError(
                f"У пользователя {self._user.user_id} уже есть кошелек для "
                f"валюты {currency_code}"
            )
        self._wallets[currency_code] = Wallet(currency_code, 0)

    def get_total_value(self, base_currency="USD") -> float:
        """
        Получить общую стоимость портфеля в указанной валюте.

        :param base_currency: код валюты, относительно которой будет посчитана
            стоимость портфеля.

        :return: стоимость портфеля в указанной валюте.

        :raises requests.exceptions.RequestException: если произошла ошибка
            при запросе к API.

        :raises ValueError: если не удалось получить курс для валюты.
        """
        rates = get_exchange_rate(base_currency)
        total_value = 0
        for currency_code, wallet in self._wallets.items():
            if currency_code == base_currency:
                total_value += wallet.balance
            else:
                rate = rates.get(currency_code)
                if rate is None:
                    raise ValueError(
                        f"Не удалось получить курс для валюты {currency_code}"
                    )
                total_value += wallet.balance / rate
        return total_value

    def get_wallet(self, currency_code) -> Optional[Wallet]:
        """
        Получить кошелек для указанной валюты.

        :param currency_code: код валюты.
        :return: кошелек для указанной валюты, если он существует, иначе None.
        """
        return self._wallets.get(currency_code)

    def dump(self) -> dict:
        return {
            ProtfolioJsonKeys.user.value: self._user,
            ProtfolioJsonKeys.wallets.value: self._wallets
        }
