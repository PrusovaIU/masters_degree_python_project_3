from dataclasses import dataclass


@dataclass
class LogRecord:
    """
    Запись лога.
    """
    #: действие:
    action: str
    #: результат выполнения действия:
    result: str
    #: тип ошибки, если произошла ошибка, иначе None:
    error_type: str | None = None
    #: сообщение об ошибке, если произошла ошибка, иначе None:
    error_message: str | None = None
    #: дополнительные данные для лога
    message: str| dict | None = None

    def __str__(self):
        if self.error_type:
            return (f"{self.action} result={self.result} "
                    f"error_type={self.error_type} "
                    f"error='{self.error_message}' msg='{self.message}'")
        else:
            return f"{self.action} result={self.result} msg='{self.message}'"
