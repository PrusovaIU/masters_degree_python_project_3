import secrets

from .models import User
from .utils import data as data_utils


class CoreError(Exception):
    pass


class UserError(CoreError):
    pass

class UserIsAlreadyExistError(UserError):
    pass


class Core:
    _USER_PASSWORD_MIN_LENGTH = 4

    def __init__(self):
        self._users: list[User] = self._load_users()

    @staticmethod
    def _load_users() -> list[User]:
        try:
            data: list[dict] = data_utils.load_data(User)
            users: list[User] = []
            for i, user in enumerate(data):
                users.append(User(**user))
        except data_utils.DataError as e:
            raise SystemError(
                f"Невозможно загрузить данные пользователей: {e}"
            )
        except TypeError as e:
            raise SystemError(
                f"Неверный формат данных: "
                f"{e} (пользователь [{i}])"
            )
        return users

    def registrate_user(self, username: str, password: str) -> User:
        """
        Регистрация нового пользователя.

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
