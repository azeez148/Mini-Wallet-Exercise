import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owned_by = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    enabled_at = models.DateTimeField(null=True)
    disabled_at = models.DateTimeField(null=True)
    balance = models.FloatField(default=0.0)


class WalletDeposit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deposited_by = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    deposited_at = models.DateTimeField(null=True)
    amount = models.FloatField(default=0.0)
    reference_id = models.TextField(unique=True)


class WalletWithdrawal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    withdrawn_by = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    withdrawn_at = models.DateTimeField(null=True)
    amount = models.FloatField(default=0.0)
    reference_id = models.TextField(unique=True)
