import secrets

import requests

from .models import User, Wallet
from .models.portfolio import Portfolio, ProtfolioJsonKeys
from .utils import data as data_utils
from .utils.currency_rates import get_exchange_rate, RatesType
from typing import TypeVar, Type, Protocol


class CoreError(Exception):
    pass


class UserError(CoreError):
    pass

class UserIsAlreadyExistError(UserError):
    pass

class UnknownUserError(UserError):
    pass


class DumpClassProtocol(Protocol):
    def dump(self) -> dict: ...


DC = TypeVar("DC", bound=DumpClassProtocol)
T = TypeVar("T")


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
    def _load_data(obj: Type[T]) -> list[T]:
        """
        Загрузка данных из файла.

        :param obj: класс объекта.
        :return: список объектов.

        :raises CoreError: если не удалось загрузить данные.
        """
        try:
            data: list[dict] = data_utils.load_data(obj)
            objs: list[T] = []
            for i, user in enumerate(data):
                objs.append(obj(**user))
        except data_utils.DataError as e:
            raise CoreError(
                f"Невозможно загрузить данные \"{obj.__name__}\": {e}"
            )
        except TypeError as e:
            raise CoreError(
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

        :raises CoreError: если не удалось сохранить данные.
        """
        dumps_data: list[dict] = [el.dump() for el in data]
        try:
            data_utils.save_data(obj, dumps_data)
        except data_utils.DataError as e:
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
        """
        try:
            portfolio = self.get_portfolio(user_id)
            rates: RatesType = get_exchange_rate(base_currency)
            data = {}
            for wallet in portfolio.wallets.values():
                data[wallet] = wallet.convert(base_currency, rates)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise CoreError(f"Неизвестная базовая валюта: {base_currency}")
            else:
                raise CoreError(f"Ошибка при получении данных: {e}")
        except requests.RequestException as e:
            raise CoreError(f"Ошибка при получении данных: {e}")
        return data

