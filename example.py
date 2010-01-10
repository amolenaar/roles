"""
Classic roles example, using proxy instances.

Based on the DCI PoC of David Byers and Serge Beaumont
(see: http://groups.google.com/group/object-composition/files)
"""

from roles import RoleType, clone


class MoneySource(object):
    __metaclass__ = RoleType

    def transfer_to(self, ctx, amount):
        if self.balance >= amount:
            self.withdraw(amount)
            ctx.sink.receive(ctx, amount)


class MoneySink(object):
    __metaclass__ = RoleType

    def receive(self, ctx, amount):
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


class Context(object):
    """Holds Context state."""
    pass


class TransferMoney(object):
    def __init__(self, source, sink):
        self.context = Context()
        print 'creating source'
        self.context.source = MoneySource(source, method=clone)
        print 'creating sink'
        self.context.sink = MoneySink(MoneySource(sink, method=clone))

    def __call__(self, amount):
        self.context.source.transfer_to(self.context, amount)


src = Account(1000)
dst = Account(0)

t = TransferMoney(src, dst)
t(100)

print src, src.balance
assert src.balance == 900
print dst, dst.balance
assert dst.balance == 100

print "We can still access the original attributes", t.context.sink.balance
assert t.context.sink.balance == 100
print "Is it still an Account?", isinstance(t.context.sink, Account)
assert isinstance(t.context.sink, Account)
print "Object equality?", dst == t.context.sink

# vim:sw=4:et:ai
