from valutatrade_hub.infra import Singleton, JsonSettingsLoader, Parameter
from pathlib import Path


class Config(JsonSettingsLoader, metaclass=Singleton):
    data_path = Parameter(Path)
    base_currency = Parameter()
