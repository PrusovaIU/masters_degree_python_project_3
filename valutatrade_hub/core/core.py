import secrets

import requests

from .models import User, Wallet, Portfolio, BuyInfo
from .utils import data as data_utils
from .utils.currency_rates import (get_exchange_rate, RatesType,
                                   CurrencyRatesError)
from typing import TypeVar, Type, Protocol, Optional
from .exceptions import CoreError


class UserError(CoreError):
    """
    Класс ошибки взаимодействия с пользователем.
    """
    pass

class UserIsAlreadyExistError(UserError):
    """
    Класс ошибки регистрации нового пользователя с уже существующим именем.
    """
    pass

class UnknownUserError(UserError):
    """
    Класс ошибки при обращении к несуществующему пользователю.
    """
    pass


class LoadDataError(CoreError):
    """
    Класс ошибки загрузки данных.
    """
    pass


class SaveDataError(CoreError):
    """
    Класс ошибки сохранения данных.
    """
    pass


class DumpClassProtocol(Protocol):
    def dump(self) -> dict: ...


class LoadClassProtocol(Protocol):
    @classmethod
    def load(cls, data: dict) -> "LoadClassProtocol": ...


DC = TypeVar("DC", bound=DumpClassProtocol)
LC = TypeVar("LC", bound=LoadClassProtocol)


class Core:
    _USER_PASSWORD_MIN_LENGTH = 4

    def __init__(self):
        self._users: list[User] = self._load_data(User)
        self._portfolios: list[Portfolio] = self._load_data(Portfolio)

    @property
    def user_names(self) -> list[str]:
        """
        :return: список имен пользователей.
        """
        return [user.username for user in self._users]

    @staticmethod
    def _load_data(obj: Type[LC]) -> list[LC]:
        """
        Загрузка данных из файла.

        :param obj: класс объекта.
        :return: список объектов.

        :raises LoadDataError: если не удалось загрузить данные.
        """
        try:
            data: list[dict] = data_utils.load_data(obj)
            objs: list[LC] = []
            for i, item in enumerate(data):
                objs.append(obj.load(item))
        except data_utils.DataError as e:
            raise LoadDataError(
                f"Невозможно загрузить данные \"{obj.__name__}\": {e}"
            )
        except (KeyError, TypeError) as e:
            raise LoadDataError(
                f"Неверный формат данных: "
                f"{e} ({obj.__name__} [{i}])"
            )
        return objs

    @staticmethod
    def _save_data(obj: Type[DC], data: list[DC]) -> None:
        """
        Сохранение данных в файл.

        :param obj: класс объекта.
        :param data: список объектов.
        :return: None.

        :raises SaveDataError: если не удалось сохранить данные.
        """
        dumps_data: list[dict] = [el.dump() for el in data]
        try:
            data_utils.save_data(obj, dumps_data)
        except (TypeError, data_utils.DataError) as e:
            raise CoreError(
                f"Невозможно сохранить данные \"{obj.__name__}\": {e}"
            )

    def registrate_user(self, username: str, password: str) -> int:
        """
        Регистрация нового пользователя.

        При успешной регистрации создается новый пользователь и его портфель.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: ID нового пользователя.

        :raises ValueError: если переданы некорректные параметры.

        :raises UserIsAlreadyExistError: если пользователь с таким именем уже
            существует.

        :raises CoreError: если не удалось создать нового пользователя
        """
        new_user = self._new_user(username, password)
        self._new_portfolio(new_user)
        return new_user.user_id

    def _new_user(self, username: str, password: str) -> User:
        """
        Создание нового пользователя.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: новый пользователь.

        :raises ValueError: если переданы некорректные параметры.

        :raises UserIsAlreadyExistError: если пользователь с таким именем уже
            существует.

        :raises CoreError: если не удалось создать нового пользователя
        """
        self._check_user_parameters(username, password)
        if username in self.user_names:
            raise UserIsAlreadyExistError(username)
        user_id: int = max(
            [user.user_id for user in self._users],
            default=0
        ) + 1
        solt: str = secrets.token_hex(32)
        user = User.new(
            user_id,
            username,
            password,
            solt
        )
        self._users.append(user)
        self._save_data(User, self._users)
        return user

    def _check_user_parameters(self, username: str, password: str) -> None:
        """
        Проверка параметров пользователя.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: None.

        :raises ValueError: если параметры пользователя не прошли проверку.
        """
        if not username:
            raise ValueError("Имя пользователя не может быть пустым")
        if not password:
            raise ValueError("Пароль не может быть пустым")
        if len(password) < self._USER_PASSWORD_MIN_LENGTH:
            raise ValueError("Пароль должен быть не короче 4 символов")

    def _new_portfolio(self, user: User) -> Portfolio:
        """
        Создание нового портфеля.

        :param user: пользователь, для которого создается портфель.
        :return: новый портфель.

        :raises CoreError: если не удалось создать новый портфель.
        """
        new_portfolio = Portfolio(user.user_id)
        self._portfolios.append(new_portfolio)
        self._save_data(Portfolio, self._portfolios)
        return new_portfolio

    def login_user(self, username: str, password: str) -> User:
        """
        Авторизация пользователя.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: пользователь.

        :raises ValueError: если передан некорректный пароль.

        :raises UnknownUserError: если пользователь с таким именем не найден.
        """
        try:
            user: User = [
                user for user in self._users if user.username == username
            ][0]
            if not user.check_password(password):
                raise ValueError("Неверный пароль")
            return user
        except IndexError:
            raise UnknownUserError(username)

    def get_portfolio(self, user_id: int) -> Portfolio:
        """
        Получение портфеля пользователя.

        :param user_id: ID пользователя.
        :return: портфель пользователя.

        :raises UnknownUserError: если портфель для указанного пользователя
            не найден.
        """
        try:
            return [
                portfolio for portfolio in self._portfolios
                if portfolio.user == user_id
            ][0]
        except IndexError:
            raise UnknownUserError(user_id)

    def get_wallets_balances(
            self,
            user_id: int,
            base_currency: str
    ) -> dict[Wallet, float]:
        """
        Получение балансов портфеля пользователя.

        Балансы всех кошельков конвертируются в указанную валюту.

        :param user_id: ID пользователя.
        :param base_currency: валюта, в которую будут конвертироваться балансы.

        :return: словарь с балансами портфеля вида
            {кошелек: конвертированный баланс}

        :raises UnknownUserError: если портфель для указанного пользователя
            не найден.

        :raises valutatrade_hub.core.utils.currency_rates.CurrencyRatesError:
            если не удалось получить курс валюты.
        """
        portfolio = self.get_portfolio(user_id)
        rates: RatesType = get_exchange_rate(base_currency)
        data = {}
        for wallet in portfolio.wallets.values():
            data[wallet] = wallet.convert(base_currency, rates)
        return data

    def buy(self, user_id: int, buy_info: BuyInfo) -> None:
        """
        Покупка валюты.

        :param user_id: ID пользователя.
        :param buy_info: информация о покупке.
        :return: None.

        :raises UnknownUserError: если портфель для указанного пользователя
            не найден.

        :raises ValueError: если переданы некорректные данные.

        :raises valutatrade_hub.core.utils.currency_rates.CurrencyRatesError:
            если не удалось получить курс валюты.

        :raises CoreError: если не удалось совершить покупку.
        """
        portfolio = self.get_portfolio(user_id)
        wallet: Optional[Wallet] = portfolio.get_wallet(buy_info.currency)
        if wallet is None:
            wallet = portfolio.add_currency(buy_info.currency)
        buy_info.before_balance = wallet.balance
        buy_info.wallet = wallet
        balance: float = wallet.deposit(buy_info.amount)
        try:
            self._save_data(Portfolio, self._portfolios)
            rates: RatesType = get_exchange_rate(buy_info.base_currency)
            buy_info.rate = rates[buy_info.currency]
        except CurrencyRatesError as e:
            print(e)
        except SaveDataError as e:
            wallet.balance -= buy_info.amount
            raise e
        else:
            buy_info.after_balance = balance

