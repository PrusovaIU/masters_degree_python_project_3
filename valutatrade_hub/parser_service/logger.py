from valutatrade_hub.logging_config.log_record import LogRecord
from dataclasses import dataclass
from valutatrade_hub.logging_config import LoggingConfig
from valutatrade_hub.infra.singleton import SingletonMeta


@dataclass
class HTTPLogRecord(LogRecord):
    url: str = ""
    response_status_code: int | None = None
    response_text: str | None = None

    def __str__(self):
        if self.error_type:
            return (f"url='{self.url}' "
                    f"response_status_code={self.response_status_code} "
                    f"response_text='{self.response_text}' "
                    f"error_type={self.error_type} "
                    f"error_message='{self.error_message}'")
        return (f"url='{self.url}' "
                f"response_status_code={self.response_status_code} "
                f"response_text='{self.response_text}'")


class Logger(LoggingConfig, metaclass=SingletonMeta):
    pass
