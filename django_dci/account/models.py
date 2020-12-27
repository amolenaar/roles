from django.db import models

# Create your models here.

class Account(models.Model):

    balance = models.DecimalField(decimal_places=2, max_digits=12)

    def withdraw(self, amount):
        print "Withdraw " + str(amount) + " from " + str(self)
        self.balance -= amount

    def deposit(self, amount):
        print "Deposit " + str(amount) + " in " + str(self)
        self.balance += amount
