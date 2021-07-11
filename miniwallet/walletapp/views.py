import datetime
from django.db import IntegrityError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import Wallet, WalletTransaction
from .serializers import WalletSerializer, WalletTransactionSerializer
from . import constants

from django.contrib.auth.models import User


class InitAPIView(APIView):
    """
    Endpoint for Initiating the API. Returns authentication token on success.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        result = {
            'data': None,
            'status': 'failed'
        }

        # Ideally this should return the existing user object.
        customer_xid = request.data.get('customer_xid')
        user_obj = User.objects.filter(username=customer_xid).first()

        # for this testing purpose only, creating a test user for furthur process.
        # Ideally this will not occur in a prod env.
        if not user_obj:
            user_obj = User.objects.create_user(customer_xid, 'test@test.com', 'testpassword')
            user_obj.last_name = 'testFirst'
            user_obj.last_name = 'testLast'
            user_obj.save()

        try:
            wallet = Wallet.objects.create(owned_by=user_obj)
            wallet.save()
        except IntegrityError:
            result['message'] = 'Wallet already created for this user.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user_obj)
        result['token'] = str(token)
        result['status'] = 'success'
        return Response(result, status=status.HTTP_201_CREATED)


class WalletAPIView(APIView):
    """
    Endpoint for Wallet operations. Returns wallet data on success.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        result = {
            'data': {},
            'status': 'failed'
        }

        wallet = User.objects.filter(username=request.user)[0].wallet

        if not wallet:
            result['message'] = 'Unexpected error.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        if not wallet.status == constants.WALLET_STATUS_ENABLED:
            result['message'] = 'Wallet is not yet enabled.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        wallet_serializer = WalletSerializer(wallet)

        result['data']['wallet'] = {}

        wallet_data = {
            'id': wallet_serializer.data['id'],
            'owned_by': wallet_serializer.data['owned_by'],
            'status': wallet_serializer.data['status'],
            'enabled_at': wallet_serializer.data['status_last_updated_at'],
            'balance': wallet_serializer.data['balance'],
        }
        result['data']['wallet'] = wallet_data
        result['status'] = 'success'

        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        result = {
            'data': {},
            'status': 'failed'
        }

        wallet = User.objects.filter(username=request.user)[0].wallet

        if not wallet:
            result['message'] = 'Unexpected error.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        if wallet.status == constants.WALLET_STATUS_ENABLED:
            result['message'] = 'Wallet is already enabled.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        wallet.status = constants.WALLET_STATUS_ENABLED
        wallet.status_last_updated_at = datetime.datetime.now()
        wallet.save()

        wallet_serializer = WalletSerializer(wallet)

        result['data']['wallet'] = {}

        wallet_data = {
            'id': wallet_serializer.data['id'],
            'owned_by': wallet_serializer.data['owned_by'],
            'status': wallet_serializer.data['status'],
            'enabled_at': wallet_serializer.data['status_last_updated_at'],
            'balance': wallet_serializer.data['balance'],
        }
        result['data']['wallet'] = wallet_data
        result['status'] = 'success'

        return Response(result, status=status.HTTP_201_CREATED)

    def patch(self, request):
        result = {
            'data': {},
            'status': 'failed'
        }

        is_disabled = request.data.get('is_disabled')

        if not is_disabled:
            result['message'] = 'Unexpected error: Parameter missing.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        if is_disabled != 'true':
            result['message'] = 'Wallet disable skipped as per params.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        wallet = User.objects.filter(username=request.user)[0].wallet

        if not wallet:
            result['message'] = 'Unexpected error.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        if not wallet.status == constants.WALLET_STATUS_ENABLED:
            result['message'] = 'Wallet is already disabled.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        wallet.status = constants.WALLET_STATUS_DISABLED
        wallet.status_last_updated_at = datetime.datetime.now()
        wallet.save()

        wallet_serializer = WalletSerializer(wallet)

        result['data']['wallet'] = {}

        wallet_data = {
            'id': wallet_serializer.data['id'],
            'owned_by': wallet_serializer.data['owned_by'],
            'status': wallet_serializer.data['status'],
            'disbled_at': wallet_serializer.data['status_last_updated_at'],
            'balance': wallet_serializer.data['balance'],
        }
        result['data']['wallet'] = wallet_data
        result['status'] = 'success'
        return Response(result, status=status.HTTP_200_OK)


class WalletDepositAPIView(APIView):
    """
    Endpoint for Deposit operations. Returns deposit data on success.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        result = {
            'data': {},
            'status': 'failed'
        }

        amount_to_deposit = float(request.data.get('amount'))
        reference_id = request.data.get('reference_id')

        if amount_to_deposit < 0.0:
            result['message'] = 'Amount should be greater than 0.0.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        wallet = User.objects.filter(username=request.user)[0].wallet

        if not wallet:
            result['message'] = 'Unexpected error.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        if not wallet.status == constants.WALLET_STATUS_ENABLED:
            result['message'] = 'Wallet is not yet enabled.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        deposit = None
        try:
            wallet.balance = wallet.balance + amount_to_deposit
            deposit = WalletTransaction.objects.create(wallet=wallet, status=True, transaction_at=datetime.datetime.now(), amount=amount_to_deposit, reference_id=reference_id, type=constants.TRANSACTION_TYPE_CREDIT)
        except IntegrityError:
            wallet.balance = wallet.balance - amount_to_deposit
            result['message'] = 'Already applied this deposit.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        finally:
            wallet.save()
            if deposit:
                deposit.save()

        if deposit:
            deposit_serializer = WalletTransactionSerializer(deposit)
            result['status'] = 'success'
            result['data']['deposit'] = {}
            deposit_data = {
                'id': deposit_serializer.data['id'],
                'deposited_by': wallet.owned_by.id,
                'status': 'success',
                'deposited_at': deposit_serializer.data['transaction_at'],
                'amount': deposit_serializer.data['amount'],
                'reference_id': deposit_serializer.data['reference_id']
            }
            result['data']['deposit'] = deposit_data

        return Response(result, status=status.HTTP_201_CREATED)


class WalletWithDrawalAPIView(APIView):
    """
    Endpoint for Withdrawal operations. Returns withdrawal data on success.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        result = {
            'data': {},
            'status': 'failed'
        }

        amount_to_withdraw = float(request.data.get('amount'))
        reference_id = request.data.get('reference_id')

        if amount_to_withdraw < 0.0:
            result['message'] = 'Amount should be greater than 0.0.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        wallet = User.objects.filter(username=request.user)[0].wallet

        withdrawal = None
        if not wallet:
            result['message'] = 'Unexpected error.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        if not wallet.status == constants.WALLET_STATUS_ENABLED:
            result['message'] = 'Wallet is not yet enabled.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        if not wallet.balance - amount_to_withdraw >= 0.0:
            result['message'] = 'Withdrawal amount exceeds existing amount.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        try:
            wallet.balance = wallet.balance - amount_to_withdraw
            withdrawal = WalletTransaction.objects.create(wallet=wallet, status=True, transaction_at=datetime.datetime.now(), amount=amount_to_withdraw, reference_id=reference_id, type=constants.TRANSACTION_TYPE_DEBIT)
        except IntegrityError:
            wallet.balance = wallet.balance + amount_to_withdraw
            result['message'] = 'Already applied this withdrawal.'
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        finally:
            wallet.save()
            if withdrawal:
                withdrawal.save()

        if withdrawal:
            withdrawal_serializer = WalletTransactionSerializer(withdrawal)
            result['status'] = 'success'
            result['data']['withdrawal'] = {}
            withdrawal_data = {
                'id': withdrawal_serializer.data['id'],
                'withdrawn_by': wallet.owned_by.id,
                'status': 'success',
                'withdrawn_at': withdrawal_serializer.data['transaction_at'],
                'amount': withdrawal_serializer.data['amount'],
                'reference_id': withdrawal_serializer.data['reference_id']
            }
            result['data']['withdrawal'] = withdrawal_data

        return Response(result, status=status.HTTP_201_CREATED)
