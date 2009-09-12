"""
Roles example.

Based on the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
"""

from roles import RoleType, clone, roles


class MoneySource(object):
    __metaclass__ = RoleType

    def transfer_to(self, sink, amount):
        if self.balance >= amount:
            self.withdraw(amount)
            sink.receive(amount)


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


def transfer_money(source, sink, amount):
    """
    The interaction.
    """
    with roles((MoneySource, source),
               (MoneySink, sink)):
        source.transfer_to(sink, amount)

src = Account(1000)
dst = Account(0)

transfer_money(src, dst, amount=100)

print src, src.balance
assert src.balance == 900
print dst, dst.balance
assert dst.balance == 100

