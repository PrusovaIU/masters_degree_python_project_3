from valutatrade_hub.parser_service.models import Storage
from pathlib import Path
from json import load, JSONDecodeError
from ..exceptions import CoreError


def load_rates(file_path: Path) -> Storage:
    """
    Загрузка данных о курсах валют из файла
    :param file_path: Путь к файлу.
    :return: Объект Storage.

    :raises JSONDecodeError: Если файл содержит невалидный JSON.
    :raises OSError: если не удалось прочитать файл.
    """
    try:
        with open(file_path) as file:
            data = load(file)
        return Storage.load(data)
    except (OSError, JSONDecodeError) as e:
        raise CoreError(f"Ошибка при загрузке данных о курсах валют: "
                        f"{e} ({e.__class__.__name__})")

