from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Optional


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
            # вместо hashed_password, как требуется в задании, передается
            # пароль, чтобы инкапсулировать логику хэширования пароля внутри
            # класса:
            password: str,
            solt: str,
            registration_date: datetime
    ):
        self._user_id = user_id
        self._username = username
        self._solt = solt
        self._registration_date = registration_date
        self._hashed_password: Optional[str] = None
        self.change_password(password)

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

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
        encoded_password = (new_password + self._solt).encode("utf-8")
        self._hashed_password = sha256(encoded_password).hexdigest()

    def dump(self) -> dict:
        """
        :return: информация о пользователе в виде словаря.
        """
        return {
            UserParameterName.user_id.value: self._user_id,
            UserParameterName.username.value: self._username,
            UserParameterName.hashed_password.value: self._hashed_password,
            UserParameterName.solt.value: self._solt,
            UserParameterName.registration_date.value: self._registration_date
        }
