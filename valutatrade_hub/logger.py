from valutatrade_hub.infra import SingletonMeta
from valutatrade_hub.logging_config import LoggingConfig


class Logger(LoggingConfig, metaclass=SingletonMeta):
    pass
