

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

    def deposit(self, amount: float) -> None:
        """
        Пополнение баланса.

        :param amount: сумма пополнения.
        :return: None.
        """
        self._balance += amount

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
