import secrets

from .models import User
from .models.portfolio import Portfolio, ProtfolioJsonKeys
from .utils import data as data_utils
from typing import TypeVar, Type, Protocol


class CoreError(Exception):
    pass


class UserError(CoreError):
    pass

class UserIsAlreadyExistError(UserError):
    pass


class DumpClassProtocol(Protocol):
    def dump(self) -> dict: ...


DC = TypeVar("DC", bound=DumpClassProtocol)


class Core:
    _USER_PASSWORD_MIN_LENGTH = 4

    def __init__(self):
        self._users: list[User] = self._load_users()
        self._portfolios: list[Portfolio] = self._load_portfolios()

    @staticmethod
    def _load_users() -> list[User]:
        """
        Загрузка данных о пользователях.

        :return: список пользователей.

        :raises CoreError: если не удалось загрузить данные о пользователях.
        """
        try:
            data: list[dict] = data_utils.load_data(User)
            objs: list[User] = []
            for i, user in enumerate(data):
                objs.append(User(**user))
        except data_utils.DataError as e:
            raise CoreError(
                f"Невозможно загрузить данные о пользователях: {e}"
            )
        except TypeError as e:
            raise CoreError(
                f"Неверный формат данных: {e} (пользователь [{i}])"
            )
        return objs

    def _load_portfolios(self) -> list[Portfolio]:
        """
        Загрузка данных о портфелях.

        :return: список портфелей.

        :raises CoreError: если не удалось загрузить данные о портфелях.
        """
        try:
            data: list[dict] = data_utils.load_data(Portfolio)
            objs: list[Portfolio] = []
            for i, portfolio in enumerate(data):
                user_id = portfolio.pop(ProtfolioJsonKeys.user.value)
                user_id = int(user_id)
                user = [
                    user for user in self._users if user.user_id == user_id
                ][0]
                objs.append(Portfolio(user, **portfolio))
        except data_utils.DataError as e:
            raise CoreError(
                f"Невозможно загрузить данные о портфелях: {e}"
            )
        except IndexError:
            raise CoreError(
                f"Пользователь с ID \"{user_id}\" не найден"
            )
        except TypeError as e:
            raise CoreError(
                f"Неверный формат данных: {e} (портфель [{i}])"
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
        if username in [user.username for user in self._users]:
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
        new_portfolio = Portfolio(user)
        self._portfolios.append(new_portfolio)
        self._save_data(Portfolio, self._portfolios)
        return new_portfolio
