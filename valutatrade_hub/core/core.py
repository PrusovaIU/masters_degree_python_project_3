import secrets

from .models import User, Portfolio, Wallet
from .utils import data as data_utils
from typing import TypeVar, Type


class CoreError(Exception):
    pass


class UserError(CoreError):
    pass

class UserIsAlreadyExistError(UserError):
    pass


T = TypeVar("T")


class Core:
    _USER_PASSWORD_MIN_LENGTH = 4

    def __init__(self):
        self._users: list[User] = self._load_data(User, "Пользователь")
        self._portfolios: list[Portfolio] = self._load_data(
            Portfolio, "Портфель"
        )

    @staticmethod
    def _load_data(obj: Type[T], obj_title: str) -> list[T]:
        """
        Загрузка данных из файла.

        :param obj: класс объекта.
        :param obj_title: название объекта.
        :return: список объектов.

        :raises SystemError: если не удалось загрузить данные.
        """
        try:
            data: list[dict] = data_utils.load_data(obj)
            objs: list[T] = []
            for i, user in enumerate(data):
                objs.append(obj(**user))
        except data_utils.DataError as e:
            raise SystemError(
                f"Невозможно загрузить данные \"{obj_title}\": {e}"
            )
        except TypeError as e:
            raise SystemError(
                f"Неверный формат данных: "
                f"{e} ({obj_title} [{i}])"
            )
        return objs


    def registrate_user(self, username: str, password: str) -> None:
        """
        Регистрация нового пользователя.

        При успешной регистрации создается новый пользователь и его портфель.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: новый пользователь.

        :raises ValueError: если переданы некорректные параметры.

        :raises UserIsAlreadyExistError: если пользователь с таким именем уже
            существует.

        :raises UserError: если не удалось создать нового пользователя
        """
        new_user = self._new_user(username, password)
        self._new_portfolio(new_user)


    def _new_user(self, username: str, password: str) -> User:
        """
        Создание нового пользователя.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: новый пользователь.

        :raises ValueError: если переданы некорректные параметры.

        :raises UserIsAlreadyExistError: если пользователь с таким именем уже
            существует.

        :raises UserError: если не удалось создать нового пользователя
        """
        self._check_user_parameters(username, password)
        if username in [user.username for user in self._users]:
            raise UserIsAlreadyExistError(username)
        user_id: int = max([user.user_id for user in self._users]) + 1
        solt: str = secrets.token_hex(32)
        user = User.new(
            user_id,
            username,
            password,
            solt
        )
        self._users.append(user)
        try:
            data_utils.save_data(User, self._users)
        except data_utils.DataError as e:
            raise UserError(f"Ошибка при сохранении данных: {e}")
        return user

    def _new_portfolio(self, user: User) -> Portfolio:
        """
        Создание нового портфеля.

        :param user: пользователь, для которого создается портфель.
        :return: новый портфель.

        :raises UserError: если не удалось создать новый портфель.
        """
        new_portfolio = Portfolio(user)
        self._portfolios.append(new_portfolio)
        try:
            data_utils.save_data(Portfolio, self._portfolios)
        except data_utils.DataError as e:
            raise UserError(
                f"Ошибка при сохранении данных о портфеле: {e}"
            )
        return new_portfolio

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
