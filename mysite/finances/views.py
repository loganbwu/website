from django.shortcuts import render
from django.views import generic
from .models import Account

# Create your views here.
class AccountListView(generic.ListView):
    model = Account

class AccountDetailView(generic.DetailView):
    model = Account
