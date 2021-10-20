"""Classic roles example, using the roles module.

Based on the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
"""

from typing import Protocol

from roles import RoleType
from roles.context import context


class Account(Protocol):
    balance: float

    def withdraw(self, amount: float) -> None:
        ...

    def deposit(self, amount: float) -> None:
        ...


class PaymentAccount:
    def __init__(self, amount):
        print("Creating a new account with balance of " + str(amount))
        self.balance = amount

    def withdraw(self, amount):
        print("Withdraw " + str(amount) + " from " + str(self))
        self.balance -= amount

    def deposit(self, amount):
        print("Deposit " + str(amount) + " in " + str(self))
        self.balance += amount


class MoneySink(metaclass=RoleType):
    def receive(self: Account, amount):
        self.deposit(amount)


class MoneySource(metaclass=RoleType):
    def transfer_to(self: Account, amount, sink: MoneySink):  # type:ignore[misc]
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
