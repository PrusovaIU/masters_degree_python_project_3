from collections.abc import Callable
from enum import Enum
from typing import Optional, Any
import re


class Commands(Enum):
    register = "register"


CommandArgsType = dict[str, Any]
CommandHandlerType = Callable[[Commands, CommandArgsType], None]


class CommandHandlerError(Exception):
    pass


class CommandHandler:
    _handlers: dict[Commands, CommandHandlerType] = {}

    def __call__(self, command: Commands):
        def decorator(func: CommandHandlerType):
            self._handlers[command] = func
            return func
        return decorator

    @staticmethod
    def _check_command_args(command_args: str) -> None:
        matching = re.match(r"^(--\w+ \w+ ?)+^", command_args)
        if not matching:
            raise ValueError("Неверный формат аргументов команды")

    @classmethod
    def parse_command_args(
            cls,
            command_args: Optional[str]
    ) -> CommandArgsType:
        """
        Парсинг аргументов команды.

        :param command_args: строка с аргументами команды.
        :return: словарь с аргументами команды вида {имя аргумента: значение}.

        :raises ValueError: если аргументы команды не соответствуют формату.
        """
        if not command_args:
            return {}
        cls._check_command_args(command_args)
        args: list[tuple[str, str]] = re.findall(
            r"--(\w+) (\w+)",
            command_args
        )
        return {arg[0]: arg[1] for arg in args}

    @classmethod
    def _get_handler(cls, command: Commands) -> CommandHandlerType:
        """
        Получение обработчика команды.

        :param command: команда.
        :return: обработчик команды.

        :raises SystemError: если обработчик для команды не зарегистрирован.
        """
        try:
            return cls._handlers[command]
        except KeyError as e:
            raise SystemError(
                f"Не зарегистрирован обработчик для команды \"{command}\""
            )

    @classmethod
    def handle(cls, command: Commands, command_args: Optional[str]) -> Any:
        """
        Выполнение команды.

        :param command: команда.
        :param command_args: аргументы команды.
        :return: результат выполнения команды.

        :raises SystemError: если обработчик для команды не зарегистрирован.

        :raises ValueError: если аргументы команды не соответствуют формату.
        """
        handler = cls._get_handler(command)
        args = cls.parse_command_args(command_args)
        return handler(command, args)


command_handler = CommandHandler
