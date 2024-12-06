from decimal import Decimal
from django.db.models import Sum
from core.models import AdStatistics
from .models import UserBalanceWithdrawal

def user_balance_processor(request):
    user_balance = Decimal('0.0')  # Initialize as Decimal

    if request.user.is_authenticated:
        # Calculate total revenue from AdStatistics
        total_revenue = (
            AdStatistics.objects.filter(user=request.user)
            .aggregate(total_revenue=Sum('revenue'))
            .get('total_revenue') or Decimal('0.0')  # Ensure it's a Decimal
        )

        # Calculate total approved withdrawals
        total_approved_withdrawals = (
            UserBalanceWithdrawal.objects.filter(user=request.user, status='APPROVED')
            .aggregate(total_approved=Sum('amount'))
            .get('total_approved') or Decimal('0.0')  # Ensure it's a Decimal
        )

        # Calculate the final user balance after subtracting approved withdrawals
        user_balance = total_revenue - total_approved_withdrawals

        # Update the user's balance if it's different from the current balance
        if request.user.balance != user_balance:
            request.user.balance = user_balance
            request.user.save(update_fields=["balance"])

    return {'user_balance': user_balance}
