from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Category(models.Model):
    """
    Category of account or transaction
    """
    name = models.CharField(max_length=255, help_text="Category of account or transaction")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Account(models.Model):
    """
    Model representing a financial account (e.g. KiwiBank Everyday)
    Belongs to a single user
    """
    name = models.CharField(max_length=255, help_text="Enter an account name (e.g. KiwiBank Everyday)")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name="category", on_delete=models.SET_NULL, null=True)

    record = {"time": [],
            "balance": []}

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """
    Model representing a transaction
    Between one or two accounts
    """
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_balance = models.DecimalField(max_digits=10, decimal_places=2)
    dr = models.ForeignKey(Account, related_name="dr", on_delete=models.SET_NULL, null=True)
    cr = models.ForeignKey(Account, related_name="cr", on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, related_name="category", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        trans_str = "Transaction %s: " % self.timestamp.strftime("%B %d, %Y")
        if self.cr:
            trans_str += self.cr + " -> "
        trans_str += "%.2f" % self.amount
        if self.dr:
            trans_str += " -> " + self.dr
        return trans_str


class Balance(models.Model):
    """
    Model representing an account's (simulated) balance over time
    """
    limit = models.Q(model=User) | models.Q(model=Account)
    entity = models.ForeignKey(ContentType, limit_choices_to=limit, on_delete=models.CASCADE)
