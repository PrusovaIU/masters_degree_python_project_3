from pathlib import Path

from valutatrade_hub.infra import JsonSettingsLoader, Parameter, SingletonMeta


class Config(JsonSettingsLoader, metaclass=SingletonMeta):
    #: путь до директории с файлами данных
    data_path = Parameter(Path)
    #: базовая валюта
    base_currency = Parameter()
    #: минимальная длина пароля пользователя
    user_passwd_min_length = Parameter(int, default=4)
    #: путь до файла с курсами валют
    rates_file_path = Parameter(Path)
    #: интервал обновления курсов валют (в минутах)
    rates_update_interval: int = Parameter(ptype=int, default=5)
