from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django_pandas.io import read_frame
from django_pandas.managers import DataFrameManager
from taggit.managers import TaggableManager
from .validators import validate_csv
import csv
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from dateutil.parser import parse
from datetime import datetime, timedelta
from django.db.models import Q
from django.utils import timezone


# Create your models here.
class Category(models.Model):
    """
    Category of account or transaction
    """
    name = models.CharField(max_length=255, help_text="Category of account or transaction", primary_key=True)
    tags = TaggableManager()

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
    name = models.CharField(max_length=255, help_text="Enter an account name (e.g. account number)", primary_key=True)
    description = models.CharField(max_length=255, help_text="Enter a description (e.g. KiwiBank Everyday)", blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    transaction_file = models.FileField(blank=True, null=True, validators=[validate_csv])

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

    def save(self, *args, **kwargs):
        super(Account, self).save(*args, **kwargs)
        print(self.transaction_file)
        if self.transaction_file:
            process_account_csv(self.transaction_file.url)
            print("Deleting file...")
            # self.FieldFile.delete()


class Transaction(models.Model):
    """
    Model representing a transaction
    Between one or two accounts
    """
    id = models.AutoField(primary_key=True)
    dr = models.ForeignKey(Account, related_name="dr", on_delete=models.SET_NULL, null=True)
    cr = models.ForeignKey(Account, related_name="cr", on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    category = models.ForeignKey(Category, related_name="category", on_delete=models.SET_NULL, null=True)
    tags = TaggableManager()

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        trans_str = "Transaction %s: " % self.timestamp.strftime("%B %d, %Y")
        if self.cr:
            trans_str += str(self.cr) + " -> "
        trans_str += "$%.2f" % self.amount
        if self.dr:
            trans_str += " -> " + str(self.dr)
        return trans_str


class Balance(models.Model):
    """
    Model representing an account's balance history at a certain time
    """
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    objects = DataFrameManager()

def process_account_csv(url):
    print("Processing", url)
    print(url)
    with open(url) as file:
        csvreader = csv.reader(file)
        csvlist = list(csvreader)
        if not csvlist[0][0] or any(csvlist[0][1:]):
            raise ValidationError(_("Uploaded CSV was not in 'KiwiBank Basic' format."))
        else:
            acc_number = csvlist[0][0]
            account = Account.objects.get(name=acc_number)
            print("Deleting old transactions...")
            print("No. transactions: ", Transaction.objects.all().count())
            # Transaction.objects.filter(Q(cr=account) or Q(dr=account)).delete()
            Transaction.objects.all().delete()
            print("No. transactions: ", Transaction.objects.all().count())
            count = 0
            for row in csvlist[1:]:
                timestamp = timezone.make_aware(parse(row[0]))
                desc = row[1].split(";")[0].strip()
                if "-" in desc and ":" in desc:
                    desc, clocktime = desc.rsplit("-", 1)
                    clocktime = clocktime.strip(" ")
                    if ":" in clocktime:
                        c = datetime.strptime(clocktime, "%H:%M")
                        delta = timedelta(hours=c.hour, minutes=c.minute)
                        # timestamp += delta
                amount = float(row[3])
                if amount <= 0:
                    dr = account
                    cr = None
                else:
                    cr = account
                    dr = None
                t = Transaction.objects.create(dr=dr, cr=cr, amount=amount, description=desc, timestamp=timestamp)
