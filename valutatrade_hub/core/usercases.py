import secrets
from pathlib import Path

from .models import User, Wallet, Portfolio, OperationInfo
from valutatrade_hub.infra.database import DatabaseManager, DataError
from .utils import currency_rates as cr
from .exceptions import CoreError
from valutatrade_hub.core.exceptions import InsufficientFundsError


class UserError(CoreError):
    """
    Класс ошибки взаимодействия с пользователем.
    """
    pass

class UserIsAlreadyExistError(UserError):
    """
    Класс ошибки регистрации нового пользователя с уже существующим именем.
    """
    pass

class UnknownUserError(UserError):
    """
    Класс ошибки при обращении к несуществующему пользователю.
    """
    pass


class UnknownWalletError(CoreError):
    """
    Класс ошибки при обращении к несуществующему кошельку.
    """
    def __init__(self, user_id: int, currency: str):
        self.user_id = user_id
        self.currency = currency

    def __str__(self):
        return (f"Не существует кошелек для пользователя {self.user_id} "
                f"в валюте {self.currency}")


class LoadDataError(CoreError):
    """
    Класс ошибки загрузки данных.
    """
    pass


class SaveDataError(CoreError):
    """
    Класс ошибки сохранения данных.
    """
    pass


class Core:
    def __init__(
            self,
            data_path: Path,
            user_passwd_min_length: int
    ):
        self._user_passwd_min_length = user_passwd_min_length
        self._db_manager = DatabaseManager(data_path)
        try:
            self._users: list[User] = self._db_manager.load_data(User)
            self._portfolios: list[Portfolio] = self._db_manager.load_data(
                Portfolio
            )
        except DataError as e:
            raise CoreError(str(e))

    @property
    def user_names(self) -> list[str]:
        """
        :return: список имен пользователей.
        """
        return [user.username for user in self._users]

    def registrate_user(self, username: str, password: str) -> int:
        """
        Регистрация нового пользователя.

        При успешной регистрации создается новый пользователь и его портфель.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: ID нового пользователя.

        :raises ValueError: если переданы некорректные параметры.

        :raises UserIsAlreadyExistError: если пользователь с таким именем уже
            существует.

        :raises CoreError: если не удалось создать нового пользователя
        """
        new_user = self._new_user(username, password)
        self._new_portfolio(new_user)
        return new_user.user_id

    def _new_user(self, username: str, password: str) -> User:
        """
        Создание нового пользователя.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: новый пользователь.

        :raises ValueError: если переданы некорректные параметры.

        :raises UserIsAlreadyExistError: если пользователь с таким именем уже
            существует.

        :raises CoreError: если не удалось создать нового пользователя
        """
        self._check_user_parameters(username, password)
        if username in self.user_names:
            raise UserIsAlreadyExistError(username)
        user_id: int = max(
            [user.user_id for user in self._users],
            default=0
        ) + 1
        solt: str = secrets.token_hex(32)
        user = User.new(
            user_id,
            username,
            password,
            solt
        )
        self._users.append(user)
        self._db_manager.save_data(User, self._users)
        return user

    def _check_user_parameters(self, username: str, password: str) -> None:
        """
        Проверка параметров пользователя.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: None.

        :raises ValueError: если параметры пользователя не прошли проверку.
        """
        if not username:
            raise ValueError("Имя пользователя не может быть пустым")
        if not password:
            raise ValueError("Пароль не может быть пустым")
        if len(password) < self._user_passwd_min_length:
            raise ValueError("Пароль должен быть не короче 4 символов")

    def _new_portfolio(self, user: User) -> Portfolio:
        """
        Создание нового портфеля.

        :param user: пользователь, для которого создается портфель.
        :return: новый портфель.

        :raises CoreError: если не удалось создать новый портфель.
        """
        new_portfolio = Portfolio(user.user_id)
        self._portfolios.append(new_portfolio)
        self._db_manager.save_data(Portfolio, self._portfolios)
        return new_portfolio

    def login_user(self, username: str, password: str) -> User:
        """
        Авторизация пользователя.

        :param username: имя пользователя.
        :param password: пароль пользователя.
        :return: пользователь.

        :raises ValueError: если передан некорректный пароль.

        :raises UnknownUserError: если пользователь с таким именем не найден.
        """
        try:
            user: User = [
                user for user in self._users if user.username == username
            ][0]
            if not user.check_password(password):
                raise ValueError("Неверный пароль")
            return user
        except IndexError:
            raise UnknownUserError(username)

    def get_portfolio(self, user_id: int) -> Portfolio:
        """
        Получение портфеля пользователя.

        :param user_id: ID пользователя.
        :return: портфель пользователя.

        :raises UnknownUserError: если портфель для указанного пользователя
            не найден.
        """
        try:
            return [
                portfolio for portfolio in self._portfolios
                if portfolio.user == user_id
            ][0]
        except IndexError:
            raise UnknownUserError(user_id)

    def get_wallets_balances(
            self,
            user_id: int,
            base_currency: str
    ) -> dict[Wallet, float]:
        """
        Получение балансов портфеля пользователя.

        Балансы всех кошельков конвертируются в указанную валюту.

        :param user_id: ID пользователя.
        :param base_currency: валюта, в которую будут конвертироваться балансы.

        :return: словарь с балансами портфеля вида
            {кошелек: конвертированный баланс}

        :raises UnknownUserError: если портфель для указанного пользователя
            не найден.

        :raises valutatrade_hub.core.utils.currency_rates.CurrencyRatesError:
            если не удалось получить курс валюты.
        """
        portfolio = self.get_portfolio(user_id)
        rates: cr.RatesType = cr.get_exchange_rate(base_currency)
        data = {}
        for wallet in portfolio.wallets.values():
            data[wallet] = wallet.convert(base_currency, rates)
        return data

    def get_wallet(
            self,
            user_id: int,
            currency: str,
            create_wallet: bool
    ) -> Wallet:
        """
        Получение кошелька пользователя.

        Если кошелек не существует, и параметр create_wallet равен True,
        то будет создан новый кошелек. Иначе будет выброшено исключение.

        :param user_id: ID пользователя.

        :param currency: код валюты.

        :param create_wallet: если не существует кошелек для указанного
            пользователя в указанной валюте, и данный параметр равен True,
            то будет создан новый кошелек.

        :return: кошелек пользователя в указанной валюте.

        :raises UnknownWalletError: если кошелек для указанного пользователя
            в указанной валюты не существует, и параметр
            create_wallet равен False.
        """
        portfolio = self.get_portfolio(user_id)
        wallet: Wallet | None = portfolio.get_wallet(currency)
        if wallet is None:
            if create_wallet:
                wallet = portfolio.add_currency(currency)
            else:
                raise UnknownWalletError(user_id, currency)
        return wallet

    def balance_operation(
            self,
            user_id: int,
            operation_info: OperationInfo,
            create_wallet: bool
    ) -> None:
        """
        Покупка валюты.

        :param user_id: ID пользователя.

        :param operation_info: информация об операции.

        :param create_wallet: если не существует кошелек для указанного
            пользователя в указанной валюте, и данный параметр равен True,
            то будет создан новый кошелек.

        :return: None.

        :raises UnknownUserError: если портфель для указанного пользователя
            не найден.

        :raises UnknownWalletError: если кошелек для указанного пользователя
            в указанной валюты не существует, и параметр
            create_wallet равен False.

        :raises ValueError: если переданы некорректные данные.

        :raises valutatrade_hub.core.utils.currency_rates.CurrencyRatesError:
            если не удалось получить курс валюты.

        :raises CoreError: если не удалось совершить покупку.
        """
        wallet = self.get_wallet(
            user_id, operation_info.currency, create_wallet
        )
        operation_info.before_balance = wallet.balance
        operation_info.wallet = wallet
        amount_abs = abs(operation_info.amount)
        if amount_abs > wallet.balance:
            raise InsufficientFundsError(
                wallet.balance, amount_abs, operation_info.currency
            )
        wallet.balance += operation_info.amount
        try:
            self._db_manager.save_data(Portfolio, self._portfolios)
            operation_info.after_balance = wallet.balance
            operation_info.rate = cr.get_rate(
                operation_info.base_currency, operation_info.currency
            )
        except cr.CurrencyRatesError as e:
            print(e)
        except SaveDataError as e:
            wallet.balance -= operation_info.amount
            raise e
