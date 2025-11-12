from abc import ABCMeta


class SingletonMeta(ABCMeta):
    """
    Метакласс для создания синглтона.

    Используется в valutatrade_hub.config

    Реализация через метакласс предпочтительнее, чем через __new__,
    потому что она более гибкая и переопределяет процесс создания класса на
    уровне метакласса. Метакласс обеспечивает
    централизованное управление экземплярами для всех классов,
    использующих его.
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    pass
