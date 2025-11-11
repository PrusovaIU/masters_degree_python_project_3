from typing import Optional

from valutatrade_hub.core import core
from .commands import Commands, CommandHandler, CommandArgsType
from valutatrade_hub.core.models import User, Wallet, Portfolio



class EngineError(Exception):
    pass


class UnknownCommandError(EngineError):
    pass


class Engine:
    def __init__(self):
        self._core = core.Core()
        self._current_user: Optional[User] = None
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
        except KeyError as e:
            print(f"Не передан обязательный параметр: {e}")
        except ValueError as e:
            print(f"Переданы некорректные данные: {e}")
        except core.UserIsAlreadyExistError as e:
            print(f"Имя пользователя \"{e}\" уже занято")
        except core.CoreError as e:
            print(e)

    @CommandHandler(Commands.login)
    def login(self, command_args: CommandArgsType) -> None:
        try:
            username = command_args["username"]
            password = command_args["password"]
            self._current_user = self._core.login_user(username, password)
            print(f"Вы вошли как \"{self._current_user.username}\"")
        except KeyError as e:
            print(f"Не передан обязательный параметр: {e}")
        except ValueError as e:
            print(e)
        except core.UnknownUserError as e:
            print(f"Пользователь \"{e}\" не найден")

    @CommandHandler(Commands.show_portfolio)
    def show_portfolio(
            self,
            command_args: Optional[CommandArgsType] = None
    ) -> None:
        if not self._current_user:
            print(f"Сначала выполните {Commands.login.value}")
            return
        default_base = "USD"
        base: str = command_args["base"] if command_args else default_base
        data = []
        try:
            wallets: dict[Wallet, float] = self._core.get_wallets_balances(
                self._current_user.user_id,
                base
            )
            for wallet, balance in wallets.items():
                data.append(
                    f"- {wallet.currency_code}: {wallet.balance} "
                    f"-> {balance} {base}"
                )
            portfolio: Portfolio = self._core.get_portfolio(
                self._current_user.user_id
            )
            total_balance: float = portfolio.get_total_value(base)
        except core.UnknownUserError:
            print(
                f"Не найден портфель для пользователя "
                f"\"{self._current_user.username}\""
            )
        except core.CoreError as e:
            print(e)
        else:
            portfolio_info = "\n".join(data) if data else "Портфель пуст"
            print(
                f"Портфель пользователя \"{self._current_user.username}\" "
                f"(база: {base}):\n"
                f"{portfolio_info}\n"
                f"--------------------------\n"
                f"ИТОГО: {total_balance:,.2f} {base}"
            )

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
