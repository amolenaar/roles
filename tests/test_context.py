
from roles import RoleType
from roles.context import context, in_context

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


class MoneySource(object):
    __metaclass__ = RoleType
    def transfer(self, amount):
        if self.balance >= amount:
            self.withdraw(amount)
            context.to_account.receive(amount)

class MoneySink(object):
    __metaclass__ = RoleType

    def receive(self, amount):
        self.deposit(amount)

class TransferMoney(object):

    def __init__(self, from_account, to_account):
        self.from_account = MoneySource(from_account)
        self.to_account = MoneySink(to_account)

    def transfer_money__with(self, amount):
        """
        The interaction.
        """
        with context(self):
            self.from_account.transfer(amount)

    @in_context
    def transfer_money__decorator(self, amount):
        """
        The interaction.
        """
        self.from_account.transfer(amount)


def test_context_context_manager_style():
    src = Account(1000)
    dst = Account(0)

    tm = TransferMoney(src, dst)

    tm.transfer_money__with(100)

    print src, src.balance
    assert src.balance == 900
    print dst, dst.balance
    assert dst.balance == 100


def test_context_decorator():
    src = Account(1000)
    dst = Account(0)

    tm = TransferMoney(src, dst)

    tm.transfer_money__decorator(100)

    print src, src.balance
    assert src.balance == 900
    print dst, dst.balance
    assert dst.balance == 100


def test_context_set_values():
    class Test(object):
        @in_context
        def test(self):
            context.foo = 1
            assert context.current_context.foo == 1

    Test().test()


# vim:sw=4:et:ai
