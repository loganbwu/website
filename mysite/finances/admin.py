from django.contrib import admin

# Register your models here.
from .models import Category, Account, Transaction

# admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Transaction)

class TransactionInlineDr(admin.TabularInline):
    model = Transaction
    max_num = 1
    fk_name = "dr"
    readonly_fields = ('description', 'timestamp', 'amount', 'dr', 'cr', 'category', 'tags')

class TransactionInlineCr(admin.TabularInline):
    model = Transaction
    max_num = 1
    fk_name = "cr"
    readonly_fields = ('description', 'timestamp', 'amount', 'dr', 'cr', 'category', 'tags')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'owner')
    exclude = ('current_balance',)
    inlines = [TransactionInlineDr, TransactionInlineCr]
