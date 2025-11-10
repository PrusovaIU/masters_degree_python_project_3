from collections.abc import Callable
from enum import Enum
from typing import Optional, Any, TypeAlias
import re
from inspect import signature


class Commands(Enum):
    register = "register"
    exit = "exit"


CommandArgsType = dict[str, Any]
CommandHandlerType: TypeAlias = (
        Callable[[CommandArgsType], None] | Callable[[], None] |
        Callable[[object, CommandArgsType], None] | Callable[[object], None]
)


class CommandHandler:
    """
    Класс для регистрации и выполнения команд.
    """
    _handlers: dict[Commands, CommandHandlerType] = {}

    def __init__(self, command: Commands):
        self._command = command

    def __call__(self, func: CommandHandlerType):
        """
        Декоратор для регистрации обработчика команды.

        :param func: обработчик команды.
        :return: декоратор для регистрации обработчика команды.
        """
        self._handlers[self._command] = func
        return func

    @staticmethod
    def _check_command_args(command_args: str) -> None:
        """
        Проверка формата аргументов команды.

        :param command_args: строка с аргументами команды.
        :return: None.

        :raises ValueError: если аргументы команды не соответствуют формату.
        """
        matching = re.match(r"^(--\w+ \w+ ?)+$", command_args)
        if not matching:
            raise ValueError("Неверный формат аргументов команды")

    @classmethod
    def _parse_command_args(
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
    def _run_handler(
            command: Commands,
            handler: CommandHandlerType,
            args: CommandArgsType,
            class_obj: object
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
        if len(handler_sign.parameters) == 0 and args:
            raise ValueError(
                f"Команда \"{command.value}\" не принимает аргументы"
            )
        handler_args = [] if class_obj is None else [class_obj]
        if args:
            handler_args.append(args)
        return handler(*handler_args)

    @classmethod
    def handle(
            cls,
            command: Commands,
            command_args: Optional[str],
            class_obj: object = None
    ) -> Any:
        """
        Выполнение команды.

        :param command: команда.

        :param command_args: аргументы команды.

        :param class_obj: объект класса, в котором определен обработчик
            команды.

        :return: результат выполнения команды.

        :raises SystemError: если обработчик для команды не зарегистрирован.

        :raises ValueError: если аргументы команды не соответствуют формату.
        """
        handler = cls._get_handler(command)
        args = cls._parse_command_args(command_args)
        return cls._run_handler(command, handler, args, class_obj)
