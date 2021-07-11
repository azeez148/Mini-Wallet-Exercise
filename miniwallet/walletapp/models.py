import uuid

from django.db import models
from django.conf import settings

from . import constants

User = settings.AUTH_USER_MODEL


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owned_by = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=constants.WALLET_STATUSES, default=constants.WALLET_STATUS_DISABLED)
    status_last_updated_at = models.DateTimeField(null=True)
    balance = models.FloatField(default=0.0)


class WalletTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.BooleanField(default=False)
    amount = models.FloatField(default=0.0)
    reference_id = models.TextField(unique=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_at = models.DateTimeField(null=True)
    type = models.CharField(max_length=50, choices=constants.TRANSACTION_TYPES, default=constants.TRANSACTION_TYPE_DEBIT)
