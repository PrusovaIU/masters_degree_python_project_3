from typing import Optional

from valutatrade_hub.core.core import Core, CoreError, UserIsAlreadyExistError
from .commands import Commands, CommandHandler, CommandArgsType


class EngineError(Exception):
    pass


class UnknownCommandError(EngineError):
    pass


class Engine:
    def __init__(self):
        self._core = Core()
        self._exit = False

    @CommandHandler(Commands.exit)
    def exit(self) -> None:
        """
        Обработчик команды exit.

        :return: None.
        """
        answer: Optional[str] = None
        while not answer:
            data = input("> Вы уверены, что хотите выйти? (y/n) ").lower()
            answer = data if data in ("y", "n") else None
        if answer == "y":
            self._exit = True

    @CommandHandler(Commands.register)
    def register(self, command_args: CommandArgsType) -> None:
        """
        Обработчик команды register.

        :param command_args: аргументы команды.
        :return: None.
        """
        try:
            username = command_args["username"]
            password = command_args["password"]
            user_id: int = self._core.registrate_user(username, password)
            print(
                f"Пользователь '{username}' зарегистрирован (id={user_id}). "
                f"Войдите: login --username {username} --password ****"
            )
        except ValueError as e:
            print(f"Переданы некорректные данные: {e}")
        except KeyError as e:
            print(f"Не передан обязательный параметр: {e}")
        except UserIsAlreadyExistError:
            print(f"Имя пользователя \"{username}\" уже занято")
        except CoreError as e:
            print(e)

    @staticmethod
    def _input() -> tuple[Commands, Optional[str]]:
        """
        Ввод команды.

        :return: кортеж из команды и аргументов.
        """
        data: Optional[str] = None
        while not data:
            data = input("> ")
        command_els = data.strip().split(" ", 1)
        command_args: str = command_els[1] if len(command_els) > 1 else None
        command = command_els[0].lower().strip()
        try:
            return Commands(command), command_args
        except ValueError:
            raise UnknownCommandError(command)

    def run(self) -> None:
        """
        Запуск интерактивного режима.

        :return: None
        """
        while not self._exit:
            try:
                command, args = self._input()
                CommandHandler.handle(command, args, self)
            except UnknownCommandError as e:
                print(f"Неизвестная команда: \"{e}\"")
        print("Завершение работы...")
