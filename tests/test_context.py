
from roles import RoleType

# Placeholder
def in_context(func):
    return func

class TransferMoney(object):

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


    def __init__(self, from_account, to_account):
        self.from_account = MoneySource(from_account)
        self.to_account = MoneySink(to_account)

    @in_context
    def transfer_money(amount):
        """
        The interaction.
        """
        with context(self):
            self.from_account.transfer(amount)

# vim:sw=4:et:ai
