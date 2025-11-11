from typing import Optional

from valutatrade_hub.core import core
from .commands import (Commands, CommandHandler, CommandArgsType,
                       CommandHandlerType)
from valutatrade_hub.core import models
from functools import wraps
from re import match


class EngineError(Exception):
    pass


class UnknownCommandError(EngineError):
    pass


def check_login(func: CommandHandlerType) -> CommandHandlerType:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._current_user:
            print(f"Сначала выполните {Commands.login.value}")
            return
        return func(self, *args, **kwargs)
    return wrapper


class Engine:
    BASE_CURRENCY = "USD"

    def __init__(self):
        self._core = core.Core()
        self._current_user: Optional[models.User] = None
        self._exit = False

    @staticmethod
    def _check_printed_char(value: str, value_title: str) -> None:
        """
        Проверяет, что строка value содержит только буквы, цифры и символы
        подчеркивания.

        :param value: проверяемая строка.
        :param value_title: название параметра.
        :return: None.

        :raises ValueError: если строка value содержит недопустимые символы.
        """
        if not match(r"^\w+$", value):
            raise ValueError(
                f"Параметр {value_title} должен содержать только буквы, цифры "
                f"и символ подчеркивания"
            )

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
            username_pn = "username"
            password_pn = "password"
            username = command_args[username_pn]
            password = command_args[password_pn]
            self._check_printed_char(username, username_pn)
            self._check_printed_char(password, password_pn)
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
        if self._current_user:
            print(f"Вы уже вошли как \"{self._current_user.username}\"")
            return
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
    @check_login
    def show_portfolio(
            self,
            command_args: Optional[CommandArgsType] = None
    ) -> None:
        base: str = command_args["base"] if command_args \
            else self.BASE_CURRENCY
        data = []
        try:
            wallets: dict[models.Wallet, float] = \
                self._core.get_wallets_balances(
                    self._current_user.user_id,
                    base
                )
            for wallet, balance in wallets.items():
                data.append(
                    f"- {wallet.currency_code}: {wallet.balance} "
                    f"-> {balance:,.2f} {base}"
                )
            portfolio: models.Portfolio = self._core.get_portfolio(
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

    @CommandHandler(Commands.buy)
    @check_login
    def buy(self, command_args: CommandArgsType) -> None:
        try:
            currency: str = command_args["currency"].upper()
            if not currency:
                raise ValueError("Не указана валюта")
            amount: float = float(command_args["amount"])
            if amount <= 0:
                raise ValueError(
                    f"Некорректная сумма покупки: {amount} <= 0"
                )
            buy_info = models.BuyInfo(amount, currency, self.BASE_CURRENCY)
            self._core.buy(self._current_user.user_id, buy_info)
        except KeyError as e:
            print(f"Не передан обязательный параметр: {e}")
        except (ValueError, core.CoreError) as e:
            print(e)
        else:
            evaluative_amount: float = buy_info.amount / buy_info.rate
            print(
                f"Покупка выполнена: {buy_info.amount:,.4f} "
                f"{buy_info.currency} по курсу {buy_info.rate:,.2f} "
                f"{self.BASE_CURRENCY}/{buy_info.currency}\n"
                f"Изменения в портфеле:\n"
                f"- {buy_info.currency}: было {buy_info.before_balance:,.4f} "
                f"-> стало {buy_info.after_balance:,.4f}\n"
                f"Оценочная стоимость покупки: "
                f"{evaluative_amount:,.2f} {self.BASE_CURRENCY}"
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
