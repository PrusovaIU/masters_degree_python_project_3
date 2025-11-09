from collections.abc import Callable
from enum import Enum
from typing import Optional, Any
import re
from inspect import signature


class Commands(Enum):
    register = "register"


CommandArgsType = dict[str, Any]
CommandHandlerType = Callable[[CommandArgsType], None] | Callable[[], None]


class CommandHandler:
    """
    Класс для регистрации и выполнения команд.
    """
    _handlers: dict[Commands, CommandHandlerType] = {}

    def __call__(self, command: Commands):
        """
        Декоратор для регистрации обработчика команды.

        :param command: команда.
        :return: декоратор для регистрации обработчика команды.
        """
        def decorator(func: CommandHandlerType):
            self._handlers[command] = func
            return func
        return decorator

    @staticmethod
    def _check_command_args(command_args: str) -> None:
        """
        Проверка формата аргументов команды.

        :param command_args: строка с аргументами команды.
        :return: None.

        :raises ValueError: если аргументы команды не соответствуют формату.
        """
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

    @staticmethod
    def run_handler(
            command: Commands,
            handler: CommandHandlerType,
            args: CommandArgsType
    ) -> Any:
        """
        Запуск обработчика команды.

        :param command: команда.
        :param handler: обработчик команды.
        :param args: аргументы команды.
        :return: результат выполнения команды.

        :raises ValueError: если аргументы команды не соответствуют формату.
        """
        handler_sign = signature(handler)
        if len(handler_sign.parameters) > 0:
            return handler(args)
        elif args:
            raise ValueError(
                f"Команда \"{command.value}\" не принимает аргументы"
            )
        else:
            return handler()

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
        return cls.run_handler(command, handler, args)


command_handler = CommandHandler
