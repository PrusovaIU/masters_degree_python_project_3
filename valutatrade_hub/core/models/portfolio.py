from typing import Optional

from .wallet import Wallet
from .user import User
from valutatrade_hub.core.utils import get_exchange_rate


class Portfolio:
    def __init__(self, user: User, wallets: dict[str, Wallet]):
        """
        Портфель пользователя.

        :param user: пользователь.

        :param wallets: словарь с кошельками пользователя вида
            {код валюты: Wallet}
        """
        self._user = user
        self._wallets = wallets

    @property
    def user(self) -> User:
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

    def get_total_value(self, base_currency='USD') -> float:
        """
        Получить общую стоимость портфеля в указанной валюте.

        :param base_currency: код валюты, относительно которой будет посчитана
            стоимость портфеля.

        :return: стоимость портфеля в указанной валюте.

        :raises requests.exceptions.RequestException: если произошла ошибка
            при запросе к API.
        """
        rates = get_exchange_rate(base_currency)
        total_value = 0
        for currency_code, wallet in self._wallets.items():
            if currency_code == base_currency:
                total_value += wallet.balance
            else:
                rate = rates[currency_code]
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
            "user": self._user.user_id,
            "wallets": [
                {currency_code: wallet.dump()}
                for currency_code, wallet in self._wallets.items()
            ]
        }
