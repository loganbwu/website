from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django_pandas.io import read_frame
from django_pandas.managers import DataFrameManager

# Create your models here.
class Category(models.Model):
    """
    Category of account or transaction
    """
    name = models.CharField(max_length=255, help_text="Category of account or transaction")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Account(models.Model):
    """
    Model representing a financial account (e.g. KiwiBank Everyday)
    Belongs to a single user
    """
    name = models.CharField(max_length=255, help_text="Enter an account name (e.g. KiwiBank Everyday)")
    description = models.CharField(max_length=255, help_text="Enter a description (e.g. Savings)")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def process_transactions(self):
        qs = self.transaction_set.all().order_by('timestamp')

    def get_balance_dataframe(self):
        qs = self.balance_set.all()
        ts = qs.to_timeseries(index='timestamp',
                values='amount')
        return ts


class Transaction(models.Model):
    """
    Model representing a transaction
    Between one or two accounts
    """
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
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
    Model representing an account's balance history at a certain time
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    objects = DataFrameManager()
