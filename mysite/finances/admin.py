from django.contrib import admin

# Register your models here.
from .models import Category, Account, Transaction

# admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Transaction)

class TransactionInlineDr(admin.TabularInline):
    model = Transaction
    fk_name = "dr"

class TransactionInlineCr(admin.TabularInline):
    model = Transaction
    fk_name = "cr"

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'owner')
    inlines=[TransactionInlineDr, TransactionInlineCr]
