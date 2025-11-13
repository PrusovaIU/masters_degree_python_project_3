from pathlib import Path

from valutatrade_hub.infra.settings import JsonSettingsLoader, Parameter
from valutatrade_hub.infra.validator import field_validator
import logging
from logging import handlers
from re import match
from typing import Literal, get_args, NamedTuple
from json import dumps


class LogRecord(NamedTuple):
    """Запись лога"""
    #: действие:
    action: str
    #: имя пользователя:
    username: str
    #: id пользователя:
    user_id: int
    #: результат выполнения действия (True - успех, False - ошибка):
    result: bool
    #: код валюты, в которой проводится операция:
    currency_code: str | None = None
    #: сумма операции (для операций с балансом):
    amount: float | None = None
    #: курс для валюты, в которой проводится операция относительно базовой
    #: валюты:
    rate: str | None = None
    #: базовая валюта:
    base: str | None = None
    #: тип ошибки, если произошла ошибка, иначе None:
    error_type: str | None = None
    #: сообщение об ошибке, если произошла ошибка, иначе None:
    error_message: str | None = None
    #: дополнительные данные для лога
    message: str | None = None



class JSONFormatter(logging.Formatter):
    """Форматтер для логов в формате JSON"""
    def format(self, record: logging.LogRecord):
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname
        }
        msg = record.msg
        if isinstance(msg, LogRecord):
            log_data.update(msg._asdict())
        else:
            log_data["message"] = msg
        return dumps(log_data)


#: типы единиц измерения для ротации логов:
TimeUnit = Literal["s", "m", "h", "d"]
SizeUnit = Literal["b", "kb", "mb", "gb", "tb"]


class Rotation(NamedTuple):
    """Ротация логов"""
    value: int
    unit: TimeUnit | SizeUnit


class LoggingConfig(JsonSettingsLoader):
    #: имя файла логов:
    log_file_name: str = Parameter(default="action.log")
    #: путь до директории с логами:
    logs_dir_path: Path = Parameter(Path)
    #: ротация логов (значение, ед. измерения):
    rotation: Rotation = Parameter()
    #: уровень логирования:
    log_level: int = Parameter(default="INFO")
    backup_count: int = Parameter(int, default=5)
    encoding: str = Parameter(default="utf-8")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger: logging.Logger | None = None

    @field_validator("rotation")
    def _validate_rotation(self, value: str) -> Rotation:
        """Валидатор для параметра rotation."""
        matching = match(r"^(\d+) ?([a-zA-Z]+)$", value)
        if not matching:
            raise ValueError(
                "Некорректное значение для параметра \"rotation\"."
            )
        float_value = int(matching.group(1))
        if float_value <= 0:
            raise ValueError(
                "Некорректное значение для параметра \"rotation\". "
                "Значение должно быть больше 0."
            )
        unit = matching.group(2).lower()
        if unit not in get_args(TimeUnit) + get_args(SizeUnit):
            raise ValueError(
                f"Некорректная единица измерения для параметра "
                f"\"rotation\". "
                f"Допустимые значения: "
                f"{', '.join(get_args(TimeUnit) + get_args(SizeUnit))}"
            )
        return Rotation(float_value, unit)

    @field_validator("log_level")
    def _validate_log_level(self, value: str) -> int:
        """Валидатор для параметра log_level."""
        values_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR
        }
        try:
            return values_map[value.lower()]
        except KeyError:
            raise ValueError(
                f"Некорректное значение для параметра \"log_level\". "
                f"Допустимые значения: {values_map.keys()}"
            )

    def logger(self, logger_name: str) -> logging.Logger:
        """
        Получение логгера.

        Если логгер не был создан, то он создается. Иначе возвращается
        уже созданный логгер.

        :param logger_name: имя логгера.
        :return: логгер.
        """
        if not self._logger:
            self.logs_dir_path.mkdir(parents=True, exist_ok=True)
            log_path: Path = self.logs_dir_path / self.log_file_name

            logger = logging.getLogger(logger_name)
            logger.setLevel(self.log_level)

            handler = self._get_log_handler(log_path)
            handler.setFormatter(JSONFormatter())

            logger.addHandler(handler)
            self._logger = logger
        return self._logger

    def _get_log_handler(self, log_path: Path) -> logging.Handler:
        """
        Создание обработчика логов.

        :param log_path: путь до файла логов.
        :return: обработчик логов.
        """
        if self.rotation.unit in get_args(TimeUnit):
            handler = handlers.TimedRotatingFileHandler(
                log_path,
                when=self.rotation.unit,
                backupCount=self.backup_count,
                encoding=self.encoding
            )
        else:
            handler = handlers.RotatingFileHandler(
                log_path,
                maxBytes=self.rotation.value,
                backupCount=self.backup_count,
                encoding=self.encoding
            )
        return handler



