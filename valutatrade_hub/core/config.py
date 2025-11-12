from valutatrade_hub.infra import SingletonMeta, JsonSettingsLoader, Parameter
from pathlib import Path


class Config(JsonSettingsLoader, metaclass=SingletonMeta):
    data_path = Parameter(Path)
    base_currency = Parameter()
