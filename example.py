"""Classic roles example, using the roles module.

Based on the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
"""

from roles import RoleType
from roles.context import context


class Account:
    def __init__(self, amount):
        print("Creating a new account with balance of " + str(amount))
        self.balance = amount
        super(Account, self).__init__()

    def withdraw(self, amount):
        print("Withdraw " + str(amount) + " from " + str(self))
        self.balance -= amount

    def deposit(self, amount):
        print("Deposit " + str(amount) + " in " + str(self))
        self.balance += amount


class MoneySource(metaclass=RoleType):
    def transfer(self: Account, amount):
        if self.balance >= amount:
            self.withdraw(amount)
            context.sink.receive(amount)


class MoneySink(metaclass=RoleType):
    def receive(self: Account, amount):
        self.deposit(amount)


class TransferMoney:
    def __init__(self, source, sink):
        self.source = source
        self.sink = sink
        self.transfer_context = context(self, source=MoneySource, sink=MoneySink)

    def perform_transfer(self, amount):
        with self.transfer_context as ctx:
            ctx.source.transfer(amount)

            print("We can still access the original attributes", self.sink.balance)
            print("Is it still an Account?", isinstance(self.sink, Account))
            assert isinstance(self.sink, Account)
            print("Object equality?", dst == self.sink)


src = Account(1000)
dst = Account(0)

t = TransferMoney(src, dst)
t.perform_transfer(100)

print(src, src.balance)
assert src.balance == 900
print(dst, dst.balance)
assert dst.balance == 100
