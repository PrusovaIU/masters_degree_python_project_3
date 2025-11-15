from collections.abc import Callable
from typing import Optional

from valutatrade_hub.core import usercases
from .commands import (Commands, CommandHandler, CommandArgsType,
                       CommandHandlerType)
from valutatrade_hub.core import models
from functools import wraps
import re
from valutatrade_hub.config import Config
from valutatrade_hub.parser_service.updater import RatesUpdater
from ..core.models.operation_info import BalanceOperationType


class EngineError(Exception):
    pass


class UnknownCommandError(EngineError):
    pass


def check_login(func: CommandHandlerType) -> Callable:
    """
    Декоратор для проверки, был ли авторизован пользователь.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._current_user:
            print(f"Сначала выполните {Commands.login.value}")
            return None
        return func(self, *args, **kwargs)
    return wrapper


class Engine:
    def __init__(self, config: Config, parser_service: RatesUpdater):
        self._core = usercases.Core(
            config.data_path,
            config.rates_file_path,
            config.user_passwd_min_length,
            parser_service,
            config.rates_update_interval
        )
        self._base_currency = config.base_currency
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
        if not re.match(r"^\w+$", value):
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
        except usercases.UserIsAlreadyExistError as e:
            print(f"Имя пользователя \"{e}\" уже занято")

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
        except usercases.UnknownUserError as e:
            print(f"Пользователь \"{e}\" не найден")

    @CommandHandler(Commands.show_portfolio)
    @check_login
    def show_portfolio(
            self,
            command_args: Optional[CommandArgsType] = None
    ) -> None:
        """
        Обработчик команды show_portfolio.

        :param command_args: аргументы команды.
        :return: None.
        """
        base: str = command_args["base"] if command_args \
            else self._base_currency
        data = []
        try:
            wallets: dict[models.Wallet, float] = \
                self._core.get_wallets_balances(
                    self._current_user.user_id,
                    base
                )
            for wallet, balance in wallets.items():
                data.append(
                    f"- {wallet.currency_code}: {wallet.balance:,.2f} "
                    f"-> {balance:,.2f} {base}"
                )
            total_balance: float = self._core.get_total_balance(
                self._current_user.user_id,
                base
            )
        except usercases.UnknownUserError:
            print(
                f"Не найден портфель для пользователя "
                f"\"{self._current_user.username}\""
            )
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
        """
        Обработчик команды buy.

        :param command_args: аргументы команды.
        :return: None.
        """
        self._balance_operation(command_args, BalanceOperationType.buy)

    @CommandHandler(Commands.sell)
    @check_login
    def sell(self, command_args: CommandArgsType) -> None:
        """
        Обработчик команды sell.

        :param command_args: аргументы команды.
        :return: None.
        """
        try:
            self._balance_operation(command_args, BalanceOperationType.sell)
        except usercases.UnknownWalletError as err:
            print(
                f"У Вас нет кошелька \"{err.currency}\". "
                f"Добавьте валюту: она создаётся автоматически при "
                f"первой покупке."
            )

    def _balance_operation(
            self,
            command_args: CommandArgsType,
            operation_type: BalanceOperationType
    ) -> None:
        """
        Обработчик операций с балансом.

        :param command_args: аргументы команды.
        :param operation_type: тип операции.
        :return: None.
        """
        try:
            currency: str = command_args["currency"].upper()
            amount: float = float(command_args["amount"])
            if amount <= 0:
                raise ValueError(
                    "Значение параметра \"amount\" должно быть больше нуля"
                )
            create_wallet = False \
                if operation_type == BalanceOperationType.sell \
                else True
            info = models.OperationInfo(
                username=self._current_user.username,
                user_id=self._current_user.user_id,
                amount=amount,
                currency_code=currency,
                base_currency=self._base_currency,
                operation_type=operation_type
            )
            self._core.balance_operation(
                self._current_user.user_id, info, create_wallet
            )
        except KeyError as e:
            print(f"Не передан обязательный параметр: {e}")
        else:
            amount = abs(info.amount)
            if info.rate:
                rate = info.rate
                evaluative_amount: float = amount / info.rate
            else:
                rate = -1
                evaluative_amount = -1
            print(
                f"{operation_type.value.capitalize()} выполнена: "
                f"{amount:,.4f} {info.currency_code} "
                f"по курсу {rate:,.2f} "
                f"{self._base_currency}/{info.currency_code}\n"
                f"Изменения в портфеле:\n"
                f"- {info.currency_code}: было {info.before_balance:,.4f} "
                f"-> стало {info.after_balance:,.4f}\n"
                f"Оценочная стоимость: "
                f"{evaluative_amount:,.2f} {self._base_currency}"
            )

    @CommandHandler(Commands.get_rate)
    def get_rate(self, command_args: CommandArgsType) -> None:
        """
        Обработчик команды get_rate.

        :param command_args: аргументы команды.
        :return: None.
        """
        try:
            from_currency: str = command_args["from"].upper()
            to_currency: str = command_args["to"].upper()
        except KeyError as e:
            print(f"Не передан обязательный параметр: {e}")
        else:
            rate, last_update = self._core.get_rate(from_currency, to_currency)
            print(
                f"Курс {from_currency} -> {to_currency}: {rate} "
                f"(обновлено: {last_update.strftime('%Y-%m-%d %H:%M:%S')})\n"
                f"Обратный курс: {1 / rate}"
            )


    @CommandHandler(Commands.update_rates)
    def update_rates(self, command_args: CommandArgsType) -> None:
        source = command_args.get("source")
        self._core.update_rates(source)

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
            except (ValueError, usercases.CoreError) as e:
                print(e)
        print("Завершение работы...")
