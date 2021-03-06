from django.conf.urls import url
from django.urls import path

from . import views


urlpatterns = [
    path('accounts/', views.AccountListView.as_view(), name='accounts'),
    path('account/<str:pk>', views.AccountDetailView.as_view(), name='account-detail')
]
