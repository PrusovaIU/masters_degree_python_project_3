

class Wallet:
    def __init__(self, currency_code: str, balance: float):
        """
        Класс кошелька.

        :param currency_code: код валюты.
        :param balance: баланс.
        """
        self.currency_code = currency_code
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = value

    def deposit(self, amount: float) -> float:
        """
        Пополнение баланса.

        :param amount: сумма пополнения.
        :return: остаток на счете.
        """
        self.balance += amount
        return self._balance

    def withdraw(self, amount: float) -> float:
        """
        Снятие средств.

        :param amount: сумма снятия.
        :return: остаток на счете.
        """
        if self._balance < amount:
            raise ValueError("Недостаточно средств")
        self._balance -= amount
        return self._balance

    def get_balance_info(self) -> dict:
        """
        :return: информация о балансе.
        """
        return {
            "currency_code": self.currency_code,
            "balance": self._balance
        }

    def convert(self, base_currency: str, rates: dict[str, float]) -> float:
        """
        Конвертация баланса по указанным курсам.

        :param base_currency: код валюты, в которую требуется конвертировать.

        :param rates: курс относительно валюты, в которую требуется
            конвертировать.

        :return: конвертированный баланс.

        :raises ValueError: если не удалось получить курс для валюты кошелька.
        """
        if base_currency == self.currency_code:
            return self.balance
        else:
            rate = rates.get(self.currency_code)
            if rate is None:
                raise ValueError(
                    f"Не удалось получить курс для валюты {self.currency_code}"
                )
            return self.balance / rate

    def dump(self) -> dict:
        return {
            "balance": self._balance
        }
