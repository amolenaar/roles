from roles import RoleType
from roles.context import context, in_context


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
    def transfer(self, amount):
        if self.balance >= amount:
            self.withdraw(amount)
            context.to_account.receive(amount)


class MoneySink(metaclass=RoleType):
    def receive(self, amount):
        self.deposit(amount)


class TransferMoney:
    def __init__(self, from_account, to_account):
        self.from_account = MoneySource(from_account)
        self.to_account = MoneySink(to_account)

    def transfer_money__with(self, amount):
        """The interaction."""
        with context(self):
            self.from_account.transfer(amount)

    @in_context
    def transfer_money__decorator(self, amount):
        """The interaction."""
        self.from_account.transfer(amount)


def test_context_context_manager_style():
    src = Account(1000)
    dst = Account(0)

    tm = TransferMoney(src, dst)

    tm.transfer_money__with(100)

    print(src, src.balance)
    assert src.balance == 900
    print(dst, dst.balance)
    assert dst.balance == 100


def test_context_decorator():
    src = Account(1000)
    dst = Account(0)

    tm = TransferMoney(src, dst)

    tm.transfer_money__decorator(100)

    print(src, src.balance)
    assert src.balance == 900
    print(dst, dst.balance)
    assert dst.balance == 100


def test_context_set_values():
    class Test:
        @in_context
        def test(self):
            context.foo = 1
            assert context.current_context.foo == 1

    Test().test()


def test_context_manager_multi_threading():
    import threading

    class ContextClass:
        def doit(self):
            with context(self):
                # Save stack to ensure it's different
                context.stack = context.__dict__.get("__stack")

    cc1 = ContextClass()
    cc2 = ContextClass()
    thread = threading.Thread(target=cc2.doit)
    thread.start()
    cc1.doit()
    thread.join()

    # ensure both stacks are different objects
    assert cc1.stack is not cc2.stack, "%d != %d" % (id(cc1.stack), id(cc2.stack))


def test_context_manager_multi_threading_nesting():
    import threading
    import time

    class ContextClass:
        def doit(self, level=100):
            if level == 0:
                context.depth = len(context.__dict__["__stack"])
            else:
                with context(self):
                    print((context.__dict__["__stack"]), level)
                    self.doit(level - 1)
                    time.sleep(0.001)

    cc1 = ContextClass()
    cc2 = ContextClass()
    thread = threading.Thread(target=cc2.doit)
    thread.start()
    cc1.doit()
    thread.join()

    # ensure both stacks are different objects
    assert cc1.depth == 100, cc1.depth
    assert cc2.depth == 100, cc2.depth
