from typing import Optional

from .wallet import Wallet
from valutatrade_hub.parser_service.models.storage import RateDictType
from enum import Enum


class PortfolioJsonKeys(Enum):
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
        return self._wallets.copy()

    def add_currency(self, currency_code: str) -> Wallet:
        """
        Добавляет кошелек для указанной валюты.

        :param currency_code: код валюты.
        :return: кошелек для указанной валюты.
        """
        if currency_code in self._wallets:
            raise ValueError(
                f"У пользователя {self._user} уже есть кошелек для "
                f"валюты {currency_code}"
            )
        new_wallet = Wallet(currency_code, 0)
        self._wallets[currency_code] = new_wallet
        return new_wallet

    def get_total_value(
            self,
            rates: RateDictType,
            base_currency="USD"
    ) -> float:
        """
        Получить общую стоимость портфеля в указанной валюте.

        :param rates: словарь с курсами валют вида {код валюты: курс}

        :param base_currency: код валюты, относительно которой будет посчитана
            стоимость портфеля.

        :return: стоимость портфеля в указанной валюте.

        :raises requests.exceptions.RequestException: если произошла ошибка
            при запросе к API.

        :raises ValueError: если не удалось получить курс для валюты.
        """
        total_value = 0
        for wallet in self._wallets.values():
            total_value += wallet.convert(base_currency, rates)
        return total_value

    def get_wallet(self, currency_code) -> Optional[Wallet]:
        """
        Получить кошелек для указанной валюты.

        :param currency_code: код валюты.
        :return: кошелек для указанной валюты, если он существует, иначе None.
        """
        return self._wallets.get(currency_code)

    @classmethod
    def load(cls, data: dict) -> "Portfolio":
        user_id = data[PortfolioJsonKeys.user.value]
        wallets_data = data[PortfolioJsonKeys.wallets.value]
        wallets = {}
        for currency_code, wallet in wallets_data.items():
            wallets[currency_code] = Wallet.load(currency_code, wallet)
        return cls(user_id, wallets)


    def dump(self) -> dict:
        return {
            PortfolioJsonKeys.user.value: self._user,
            PortfolioJsonKeys.wallets.value: {
                wallet.currency_code: wallet.dump()
                for wallet in self._wallets.values()
            }
        }
