import json
from pathlib import Path
from typing import Protocol, Type, TypeVar


class DumpClassProtocol(Protocol):
    def dump(self) -> dict: ...


class LoadClassProtocol(Protocol):
    @classmethod
    def load(cls, data: dict) -> "LoadClassProtocol": ...


DC = TypeVar("DC", bound=DumpClassProtocol)
LC = TypeVar("LC", bound=LoadClassProtocol)


class DataError(Exception):
    pass


class FileError(DataError):
    def __init__(self, file_path: Path, obj: type, message: str | Exception):
        self._file_path = file_path
        self._obj = obj.__name__
        self._message = message if isinstance(message, str) else str(message)


class LoadDataError(FileError):
    def __str__(self):
        return (f"Не удалось загрузить данные {self._obj} из файла "
                f"\"{self._file_path}\": {self._message}")


class SaveDataError(FileError):
    def __str__(self):
        return (f"Не удалось сохранить данные {self._obj} в файл "
                f"\"{self._file_path}\": {self._message}")


class DatabaseManager:
    """
    Класс для работы с файлами.

    :param dir_path: путь к директории с файлами.
    """
    def __init__(self, dir_path: Path):
        self._dir_path = dir_path

    def _form_path(self, obj: type) -> Path:
        """
        Формирование пути к файлу с данными.

        :param obj: класс объектов, список которых нужно загрузить/сохранить.
        :return: путь к файлу со списком объектов.
        """
        return self._dir_path / f"{obj.__name__.lower()}.json"

    def read_file(self, obj: type) -> list:
        """
        Загрузка данных из файла.

        :param obj: класс объектов, список которых нужно загрузить.

        :return: список объектов.
        """
        path = self._form_path(obj)
        data = []
        try:
            if not path.exists():
                with open(path, "w") as f:
                    json.dump(data, f)
            else:
                with open(path, "r") as f:
                    data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise LoadDataError(path, obj, e)
        return data

    def write_file(self, obj: type, data: list) -> None:
        """
        Сохранение данных в файл.

        :param obj: класс объектов, список которых нужно сохранить.
        :param data: список объектов для сохранения.
        :return: None.
        """
        path = self._form_path(obj)
        try:
            with open(path, "w") as f:
                json.dump(data, f)
        except OSError as e:
            raise SaveDataError(path, obj, e)

    def load_data(self,obj: Type[LC]) -> list[LC]:
        """
        Загрузка данных из файла.

        :param obj: класс объекта.

        :return: список объектов.

        :raises LoadDataError: если не удалось загрузить данные.
        """
        try:
            data: list[dict] = self.read_file(obj)
            objs: list[LC] = []
            for i, item in enumerate(data):
                objs.append(obj.load(item))
        except (KeyError, TypeError) as e:
            raise DataError(
                f"Неверный формат данных: "
                f"{e} ({obj.__name__} [{i}])"
            )
        return objs

    def save_data(self, obj: Type[DC], data: list[DC]) -> None:
        """
        Сохранение данных в файл.

        :param obj: класс объекта.
        :param data: список объектов.
        :return: None.

        :raises SaveDataError: если не удалось сохранить данные.
        """
        dumps_data: list[dict] = [el.dump() for el in data]
        try:
            self.write_file(obj, dumps_data)
        except TypeError as e:
            raise DataError(
                f"Невозможно сохранить данные \"{obj.__name__}\": {e}"
            )
