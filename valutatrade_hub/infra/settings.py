import json
import toml
from pathlib import Path
from typing import Any
from abc import ABCMeta, abstractmethod


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SettingsLoaderError(Exception):
    pass


class UnknownParameterError(SettingsLoaderError):
    pass


class SettingsLoader(metaclass=ABCMeta):
    """
    Абстрактный класс для загрузки настроек из файла

    :param settings_file: Путь к файлу настроек.
    """
    def __init__(self, settings_file: Path):
        self._path = settings_file
        self._settings: dict[str, Any] = {}

    @abstractmethod
    def _parse_file(self, content: str) -> dict[str, Any]:
        """
        Парсинг содержимого файла настроек.

        :param content: содержимое файла настроек.
        :return: словарь с настройками вида {название параметра: значение}.

        :raises SettingsLoaderError: если файл настроек имеет неверный формат.
        """
        pass

    def load(self) -> None:
        """
        Загрузка настроек из файла.

        :return: None.
        """
        try:
            with self._path.open() as f:
                content: str = f.read()
            self._settings = self._parse_file(content)
        except OSError:
            raise SettingsLoaderError(
                f"Не удалось прочитать файл настроек \"{self._path}\""
            )

    class _NotSet:
        pass

    def get(self, key: str, default: Any = _NotSet) -> Any:
        """
        Получение значения параметра настроек.

        :param key: название параметра.
        :param default: значение по умолчанию.
        :return: значение параметра.

        :raises UnknownParameterError: если параметр не найден и не указано
            значение по умолчанию.
        """
        try:
            return self._settings[key]
        except KeyError as e:
            if default is self._NotSet:
                raise UnknownParameterError(e)
            return default


class JsonSettingsLoader(SettingsLoader):
    """
    Класс для загрузки настроек из JSON-файла.
    """
    def _parse_file(self, content: str) -> dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise SettingsLoaderError(
                f"Файл настроек \"{self._path}\" имеет неверный формат"
            )


class TOMLSettingsLoader(SettingsLoader):
    """
    Класс для загрузки настроек из TOML-файла.
    """
    def _parse_file(self, content: str) -> dict[str, Any]:
        try:
            data = toml.loads(content)
            return data.get("tool", {}).get("valutatrade", {})
        except toml.TomlDecodeError as e:
            raise SettingsLoaderError(
                f"Файл настроек \"{self._path}\" имеет неверный формат: {e}"
            )
