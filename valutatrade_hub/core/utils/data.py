import json
from pathlib import Path


class DataError(Exception):
    pass


class LoadDataError(DataError):
    pass


class SaveDataError(DataError):
    pass


def get_project_root() -> Path:
    """
    Возвращает абсолютный путь к корню проекта.

    Предполагается, что структура:
    project_root/
    └── valutatrade_hub/
        └── core/
            └── utils/
                └── data.py

    Тогда корень — это три уровня вверх от этого файла.
    """
    # Получаем путь к текущему файлу
    current_file = Path(__file__).resolve()
    # Поднимаемся на 3 уровня вверх:
    # utils → core → valutatrade_hub → project_root
    return current_file.parent.parent.parent.parent


def _form_path(obj: type) -> Path:
    """
    Формирование пути к файлу с данными.

    :param obj: класс объектов, список которых нужно загрузить/сохранить.
    :return: путь к файлу со списком объектов.
    """
    return get_project_root() / "data" / f"{obj.__name__.lower()}.json"


def load_data(obj: type) -> list:
    """
    Загрузка данных из файла.

    :param obj: класс объектов, список которых нужно загрузить.
    :return: список объектов.
    """
    path = _form_path(obj)
    data = []
    try:
        if not path.exists():
            with open(path, "w") as f:
                json.dump(data, f)
        else:
            with open(path, "r") as f:
                data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise LoadDataError(
            f"Ошибка при загрузке данных из файла {path}: {e}"
        )
    return data


def save_data(obj: type, data: list) -> None:
    """
    Сохранение данных в файл.

    :param obj: класс объектов, список которых нужно сохранить.
    :param data: список объектов для сохранения.
    :return: None.
    """
    path = _form_path(obj)
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except OSError as e:
        raise SaveDataError(
            f"Ошибка при сохранении данных в файл {path}: {e}"
        )
