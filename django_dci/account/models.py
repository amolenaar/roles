from django.db import models

# Create your models here.


class Account(models.Model):
    balance = models.DecimalField(decimal_places=2, max_digits=12)

    def withdraw(self, amount):
        print(f"Withdraw {amount} from {self}")
        self.balance -= amount

    def deposit(self, amount):
        print(f"Deposit {amount} in {self}")
        self.balance += amount
