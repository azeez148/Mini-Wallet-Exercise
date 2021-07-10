from rest_framework import serializers
from .models import Wallet, WalletDeposit, WalletWithdrawal

class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ('id', 'owned_by', 'status', 'enabled_at', 'disabled_at', 'balance')


class WalletDepositSerializer(serializers.ModelSerializer):

    class Meta:
        model = WalletDeposit
        fields = ('id', 'deposited_by', 'status', 'deposited_at', 'reference_id', 'amount')


class WalletWithdrawalSerializer(serializers.ModelSerializer):

    class Meta:
        model = WalletWithdrawal
        fields = ('id', 'withdrawn_by', 'status', 'withdrawn_at', 'reference_id', 'amount')
