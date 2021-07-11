from rest_framework import serializers
from .models import Wallet, WalletTransaction


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ('id', 'owned_by', 'status', 'status_last_updated_at', 'balance')


class WalletTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WalletTransaction
        fields = ('id', 'wallet', 'transaction_at', 'reference_id', 'amount', 'type', 'status')
