from abc import ABCMeta


class SingletonMeta(ABCMeta):
    """
    Метакласс для создания синглтона.

    Используется в core.config
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    pass
