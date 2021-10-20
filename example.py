"""Classic roles example, using the roles module.

Based on the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
"""

from typing import Protocol, runtime_checkable

from roles import RoleType
from roles.context import context


@runtime_checkable
class Account(Protocol):
    balance: int

    def withdraw(self, amount: int) -> None:
        ...

    def deposit(self, amount: int) -> None:
        ...


class PaymentAccount:
    def __init__(self, amount: int) -> None:
        print("Creating a new account with balance of " + str(amount))
        self.balance = amount

    def withdraw(self, amount: int) -> None:
        print("Withdraw " + str(amount) + " from " + str(self))
        self.balance -= amount

    def deposit(self, amount: int) -> None:
        print("Deposit " + str(amount) + " in " + str(self))
        self.balance += amount


class MoneySink(metaclass=RoleType):
    def receive(self, amount: int):
        assert isinstance(self, Account)
        self.deposit(amount)


class MoneySource(metaclass=RoleType):
    def transfer_to(self, amount: int, sink: MoneySink):
        assert isinstance(self, Account)
        if self.balance >= amount:
            self.withdraw(amount)
            sink.receive(amount)


class TransferMoney:
    def __init__(self, source: Account, sink: Account):
        self.source = source
        self.sink = sink

    def perform_transfer(self, amount):
        with context(self, source=MoneySource, sink=MoneySink) as ctx:
            ctx.source.transfer_to(amount, ctx.sink)

            print("We can still access the original attributes", self.sink.balance)
            print("Is it still an Account?", isinstance(self.sink, PaymentAccount))
            assert isinstance(self.sink, PaymentAccount)
            print("Object equality?", dst == self.sink)


if __name__ == "__main__":
    src = PaymentAccount(1000)
    dst = PaymentAccount(0)

    t = TransferMoney(src, dst)
    t.perform_transfer(100)

    print(src, src.balance)
    assert src.balance == 900
    print(dst, dst.balance)
    assert dst.balance == 100
