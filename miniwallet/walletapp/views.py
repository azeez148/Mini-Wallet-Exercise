import datetime
from django.db import IntegrityError

from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import Wallet, WalletDeposit, WalletWithdrawal
from .serializers import WalletDepositSerializer, WalletSerializer, WalletWithdrawalSerializer

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
            return Response(result)

        token, created = Token.objects.get_or_create(user=user_obj)
        print (str(token))
        result['token'] = str(token)
        result['status'] = 'success'
        return Response(result)


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

        if not wallet.status:
            result['message'] = 'Wallet is not yet enabled.'
            return Response(result)
        
        wallet_serializer = WalletSerializer(wallet)

        result['data']['wallet'] = wallet_serializer.data
        return Response(result)

    def post(self, request):
        result = {
            'data': {},
            'status': 'failed'
        }

        wallet = User.objects.filter(username=request.user)[0].wallet       

        if wallet.status:
            result['message'] = 'Wallet is already enabled.'
            return Response(result)
        
        wallet.status = True
        wallet.enabled_at = datetime.datetime.now()
        wallet.disabled_at = None
        wallet.save()

        wallet_serializer = WalletSerializer(wallet)

        result['status'] = 'success'
        result['data']['wallet'] = wallet_serializer.data
        return Response(result)

    def patch(self, request):
        result = {
            'data': {},
            'status': 'failed'
        }

        wallet = User.objects.filter(username=request.user)[0].wallet       

        if not wallet.status:
            result['message'] = 'Wallet is already disabled.'
            return Response(result)
        
        wallet.status = False
        wallet.disabled_at = datetime.datetime.now()
        wallet.enabled_at = None
        wallet.save()

        wallet_serializer = WalletSerializer(wallet)

        result['status'] = 'success'
        result['data']['wallet'] = wallet_serializer.data
        return Response(result)


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

        if amount_to_deposit < 0.0 :
            result['message'] = 'Amount should be greater than 0.0.'
            return Response(result)

        wallet = User.objects.filter(username=request.user)[0].wallet
        deposit = None
        if wallet:
            try:
                wallet.balance = wallet.balance + amount_to_deposit
                deposit = WalletDeposit.objects.create(deposited_by=wallet, status=True, deposited_at=datetime.datetime.now(), amount=amount_to_deposit, reference_id=reference_id)
            except IntegrityError:
                wallet.balance = wallet.balance - amount_to_deposit
                result['message'] = 'Already applied this deposit.'
                return Response(result)
            finally:
                wallet.save()
                if deposit:
                    deposit.save()

        if deposit:
            deposit_serializer = WalletDepositSerializer(deposit)
            result['status'] = 'success'
            result['data']['deposit'] = deposit_serializer.data

        return Response(result)


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

        if amount_to_withdraw < 0.0 :
            result['message'] = 'Amount should be greater than 0.0.'
            return Response(result)

        wallet = User.objects.filter(username=request.user)[0].wallet

        withdrawal = None
        if not wallet:
            result['message'] = 'Unexpected error.'
            return Response(result)

        if not wallet.balance - amount_to_withdraw >= 0.0 :
            result['message'] = 'Withdrawal amount exceeds existing amount.'
            return Response(result)

        try:
            wallet.balance = wallet.balance - amount_to_withdraw
            withdrawal = WalletWithdrawal.objects.create(withdrawn_by=wallet, status=True, withdrawn_at=datetime.datetime.now(), amount=amount_to_withdraw, reference_id=reference_id)
        except IntegrityError:
            wallet.balance = wallet.balance + amount_to_withdraw
            result['message'] = 'Already applied this withdrawal.'
            return Response(result)
        finally:
            wallet.save()
            if withdrawal:
                withdrawal.save()

        if withdrawal:
            withdrawal_serializer = WalletWithdrawalSerializer(withdrawal)
            result['status'] = 'success'
            result['data']['withdrawal'] = withdrawal_serializer.data

        return Response(result)
