"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from models import Account

from roles.django import ModelRoleType
from roles.context import context
from contextlib import nested


class MoneySource(object):
    __metaclass__ = ModelRoleType

    def transfer(self, amount):
        if self.balance >= amount:
            self.withdraw(amount)
            context.sink.receive(amount)


class MoneySink(object):
    __metaclass__ = ModelRoleType

    def receive(self, amount):
        self.deposit(amount)


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
            #print "Object equality?", dst == self.sink
        self.source.save()
        self.sink.save()


class MoneyTransferTest(TestCase):

    def test_basic_addition(self):
        """
        Test roles on Django model classes.
        """
        src = Account(balance=1000)
        dst = Account(balance=0)
        src.save()
        dst.save()

        accounts = Account.objects.all()
        assert len(accounts) == 2
        assert accounts[0].balance == 1000, accounts[0].balance
        assert accounts[1].balance == 0, accounts[1].balance
        ctx = TransferMoney(src, dst)

        ctx.transfer_money(amount=100)

        print src, src.balance
        assert src.balance == 900
        print dst, dst.balance
        assert dst.balance == 100

        accounts = Account.objects.all()
        assert accounts[0].balance == 900, accounts[0].balance
        assert accounts[1].balance == 100, accounts[1].balance



# vim:sw=4:et:ai
