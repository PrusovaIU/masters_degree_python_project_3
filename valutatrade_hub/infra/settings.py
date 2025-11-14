import json
from collections.abc import Callable

import toml
from pathlib import Path
from typing import Any, NamedTuple
from abc import ABCMeta, abstractmethod
from .validator import FieldValidatorType, FieldValidator


class SettingsLoaderError(Exception):
    pass


class UnknownParameterError(SettingsLoaderError):
    pass


class _NotSet:
    pass


class Parameter(NamedTuple):
    ptype: type = str
    default: Any = _NotSet
    alias: str | None = None


class SettingsLoader(metaclass=ABCMeta):
    """
    Абстрактный класс для загрузки настроек из файла

    :param settings_file: Путь к файлу настроек.
    """
    def __init__(self, settings_file: str | Path):
        if isinstance(settings_file, str):
            settings_file = Path(settings_file)
        self._path = settings_file
        self._settings: dict[str, Any] = {}
        self._is_loaded = False

    @property
    def path(self) -> Path:
        return self._path

    @classmethod
    def parameters(cls) -> dict[str, 'Parameter']:
        params = {}
        for base_cls in cls.__mro__:
            for name, attr in base_cls.__dict__.items():
                if (isinstance(attr, Parameter)
                        and not name.startswith("_")
                        and name not in params):
                    params[name] = attr
        return params

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
            if self._is_loaded:
                raise SettingsLoaderError("Настройки уже загружены")
            with self._path.open() as f:
                content: str = f.read()
            parsed_content: dict[str, Any] = self._parse_file(content)
            self._settings = self._form_settings(parsed_content)
        except OSError:
            raise SettingsLoaderError(
                f"Не удалось прочитать файл настроек \"{self._path}\""
            )
        else:
            self._is_loaded = True

    def _form_settings(self, parsed_content: dict[str, Any]) -> dict[str, Any]:
        """
        Формирование словаря с настройками.

        :param parsed_content: словарь с параметрами, полученный из файла.
        :return: словарь с настройками.

        :raises UnknownParameterError: если параметр обязательный и не найден
            в parsed_content.
        """
        settings = {}
        for name, param in self.parameters().items():
            alias = param.alias or name
            if (not alias in parsed_content
                    and param.default is _NotSet):
                raise UnknownParameterError(
                    f"Не найден параметр \"{name}\" в файле "
                    f"настроек \"{self._path}\""
                )
            value = parsed_content.get(alias, param.default)
            ptype_value = param.ptype(value)
            validated_value = self._validate(ptype_value, name)
            settings[name] = validated_value
            setattr(self, name, validated_value)
        return settings


    def _validate(self, value: Any, field_name: str) -> Any:
        """
        Валидация значения параметра.

        :param value: значение параметра.
        :param field_name: имя параметра.
        :return: валидированное значение параметра.

        :raises ValidationError: если значение параметра не прошло валидацию.
        """
        mro = self.__class__.__mro__
        validator: FieldValidatorType = \
            FieldValidator.validator(mro, field_name)
        if validator:
            try:
                value = validator(self, value)
            except Exception as err:
                raise ValueError(
                    f"Невалидный параметр \"{field_name}\": {err}"
                )
        return value

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
            if default is _NotSet:
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
