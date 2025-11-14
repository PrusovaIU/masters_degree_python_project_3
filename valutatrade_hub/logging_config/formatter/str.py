import logging


class StrFormatter(logging.Formatter):
    """Форматтер для логов в строковом формате"""
    def format(self, record: logging.LogRecord):
        log = (f"{record.levelname} "
               f"{self.formatTime(record, '%Y-%m-%dT%H:%M:%S')} "
               f"{str(record.msg)}")
        return log
