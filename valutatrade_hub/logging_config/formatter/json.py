import logging
from json import dumps

from ..log_record import LogRecord


class JSONFormatter(logging.Formatter):
    """Форматтер для логов в формате JSON"""
    def format(self, record: logging.LogRecord):
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname
        }
        msg = record.msg
        if isinstance(msg, LogRecord):
            log_data.update(msg.__dict__)
        else:
            log_data["message"] = msg
        return dumps(log_data)
