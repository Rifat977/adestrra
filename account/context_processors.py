from decimal import Decimal
from django.db.models import Sum
from core.models import AdStatistics
from .models import UserBalanceWithdrawal, Settings

def user_balance_processor(request):
    user_balance = Decimal('0.0')  

    if request.user.is_authenticated:
        total_revenue = (
            AdStatistics.objects.filter(user=request.user)
            .aggregate(total_revenue=Sum('revenue'))
            .get('total_revenue') or Decimal('0.0') 
        )

        total_approved_withdrawals = (
            UserBalanceWithdrawal.objects.filter(user=request.user, status='APPROVED')
            .aggregate(total_approved=Sum('amount'))
            .get('total_approved') or Decimal('0.0') 
        )

        user_balance = total_revenue - total_approved_withdrawals

        if request.user.balance != user_balance:
            request.user.balance = user_balance
            request.user.save(update_fields=["balance"])

    return {'user_balance': user_balance}

def setting_processor(request):
    setting = Settings.objects.first()
    return {'setting': setting}