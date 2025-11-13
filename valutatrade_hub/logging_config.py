from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from valutatrade_hub.infra.settings import JsonSettingsLoader, Parameter
from valutatrade_hub.infra.validator import field_validator
import logging
from logging import handlers
from re import match
from typing import Literal, get_args, NamedTuple
from datetime import datetime


# class LogRecord(NamedTuple):
#     timestamp: datetime
#     level: l



class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "action": getattr(record, "action", None),
            "username": getattr(record, "username", None),
            "user_id": getattr(record, "user_id", None),
            "currency_code": getattr(record, "currency_code", None),
            "amount": getattr(record, "amount", None),
            "rate": getattr(record, "rate", None),
            "base": getattr(record, "base", None),
            "result": getattr(record, "result", "OK"),
        }
        if hasattr(record, "verbose") and record.verbose:
            log_data["verbose"] = record.verbose
        if hasattr(record, "error_type"):
            log_data["error_type"] = record.error_type
        if hasattr(record, "error_message"):
            log_data["error_message"] = record.error_message


TimeUnit = Literal["s", "m", "h", "d"]
SizeUnit = Literal["b", "kb", "mb", "gb", "tb"]


class Rotation(NamedTuple):
    value: int
    unit: TimeUnit | SizeUnit


class LoggingConfig(JsonSettingsLoader):
    #: имя файла логов:
    log_file_name: str = Parameter(str, default="action.log")
    #: путь до директории с логами:
    logs_dir_path: Path = Parameter(Path)
    #: ротация логов (значение, ед. измерения):
    rotation: Rotation = Parameter()
    #: уровень логирования:
    log_level: int = Parameter(default="INFO")
    backup_count: int = Parameter(default=5)
    encoding: str = Parameter(default="utf-8")

    @staticmethod
    @field_validator("rotation")
    def _validate_rotation(value: str) -> Rotation:
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
                f"{get_args(TimeUnit) + get_args(SizeUnit)}"
            )
        return Rotation(float_value, unit)

    @staticmethod
    @field_validator("log_level")
    def _validate_log_level(value: str) -> int:
        """Валидатор для параметра log_level."""
        values_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR
        }
        try:
            return values_map[value]
        except KeyError:
            raise ValueError(
                f"Некорректное значение для параметра \"log_level\". "
                f"Допустимые значения: {values_map.keys()}"
            )

    def logger(self, logger_name: str) -> logging.Logger:
        self.logs_dir_path.mkdir(parents=True, exist_ok=True)
        log_path: Path = self.logs_dir_path / self.log_file_name

        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)

        handler = self._get_log_handler(log_path)
        handler.setFormatter(JSONFormatter())

        logger.addHandler(handler)
        return logger

    def _get_log_handler(self, log_path: Path) -> logging.Handler:
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



