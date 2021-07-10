from django.conf.urls import url
from .views import InitAPIView, WalletAPIView, WalletDepositAPIView, WalletWithDrawalAPIView

urlpatterns = [
    url(r'^init/',  InitAPIView.as_view()),
    url(r'^wallet/deposits/',  WalletDepositAPIView.as_view()),
    url(r'^wallet/withdrawals/',  WalletWithDrawalAPIView.as_view()),
    url(r'^wallet/',  WalletAPIView.as_view()),
]
