"""
Roles example, using the rolecontext decorator.

Based on the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
"""

from roles import RoleType
from roles.context import context
from contextlib import nested

class MoneySource(object):
    __metaclass__ = RoleType

    def transfer(self, amount):
        if self.balance >= amount:
            self.withdraw(amount)
            context.sink.receive(amount)


class MoneySink(object):
    __metaclass__ = RoleType

    def receive(self, amount):
        self.deposit(amount)


class Account(object):

    def __init__(self, amount):
        print "Creating a new account with balance of " + str(amount)
        self.balance = amount
        super(Account, self).__init__()

    def withdraw(self, amount):
        print "Withdraw " + str(amount) + " from " + str(self)
        self.balance -= amount

    def deposit(self, amount):
        print "Deposit " + str(amount) + " in " + str(self)
        self.balance += amount


class TransferMoney(object):

    def __init__(self, source, sink):
        self.source = source
        self.sink = sink

    def transfer_money(self, amount):
        """
        The interaction.
        """
        with nested(context(self),
                    MoneySource.played_by(self.source),
                    MoneySink.played_by(self.sink)):
            self.source.transfer(amount)
            print "We can still access the original attributes", self.sink.balance
            print "Is it still an Account?", isinstance(self.sink, Account)
            print "Object equality?", dst == self.sink


src = Account(1000)
dst = Account(0)

ctx = TransferMoney(src, dst)

ctx.transfer_money(amount=100)

print src, src.balance
assert src.balance == 900
print dst, dst.balance
assert dst.balance == 100


# vim:sw=4:et:ai
