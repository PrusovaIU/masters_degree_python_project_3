from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Optional
from valutatrade_hub.core.utils.data import save_data


class UserParameterName(Enum):
    user_id = "user_id"
    username = "username"
    solt = "solt"
    hashed_password = "hashed_password"
    registration_date = "registration_date"


class User:
    def __init__(
            self,
            user_id: int,
            username: str,
            solt: str,
            registration_date: datetime | str,
            hashed_password: Optional[str] = None
    ):
        """
        Класс пользователя.

        :param user_id: ID пользователя.
        :param username: имя пользователя.
        :param solt: случайная строка для хэширования пароля.
        :param registration_date: дата регистрации пользователя.
        :param hashed_password: хэшированный пароль пользователя.
        """
        self._user_id = user_id
        self._username = username
        self._solt = solt
        if isinstance(registration_date, str):
            registration_date = datetime.fromisoformat(registration_date)
        self._registration_date = registration_date
        self._hashed_password: Optional[str] = hashed_password

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    @classmethod
    def new(
            cls,
            user_id: int,
            username: str,
            password: str,
            solt: str
    ) -> "User":
        """
        Создание нового пользователя.

        :param user_id: ID пользователя.
        :param username: имя пользователя.
        :param password: пароль пользователя.
        :param solt: случайная строка для хэширования пароля.
        :return: новый пользователь.
        """
        registration_date = datetime.now()
        new_user = cls(
            user_id,
            username,
            solt,
            registration_date
        )
        new_user.change_password(password)
        return new_user


    def get_user_info(self) -> dict:
        """
        :return: информация о пользователе.
        """
        return {
            UserParameterName.user_id.value: self._user_id,
            UserParameterName.username.value: self._username,
            UserParameterName.registration_date.value: self._registration_date
        }

    def change_password(self, new_password: str) -> None:
        """
        Изменение пароля пользователя.

        :param new_password: новый пароль.
        :return: None.
        """
        self._hashed_password = self._hash_password(new_password)

    def _hash_password(self, password: str) -> str:
        """
        Хэширование пароля.

        :param password: пароль.
        :return: хэшированный пароль.
        """
        encoded_password = (password + self._solt).encode("utf-8")
        return sha256(encoded_password).hexdigest()

    def check_password(self, password: str) -> bool:
        """
        Проверка пароля.

        :param password: пароль.
        :return: True, если пароль верный, иначе False.
        """
        hash_password = self._hash_password(password)
        return hash_password == self._hashed_password

    def dump(self) -> dict:
        """
        :return: информация о пользователе в виде словаря.
        """
        return {
            UserParameterName.user_id.value: self._user_id,
            UserParameterName.username.value: self._username,
            UserParameterName.hashed_password.value: self._hashed_password,
            UserParameterName.solt.value: self._solt,
            UserParameterName.registration_date.value:
                self._registration_date.isoformat()
        }
