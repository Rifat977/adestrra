from decimal import Decimal
from django.db.models import Sum
from core.models import AdStatistics
from .models import UserBalanceWithdrawal, Settings
from core.models import Notice

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

def notices_processor(request):
    notices = Notice.objects.all().order_by('-id')[:5]
    return {'bel_notices': notices}

from datetime import timedelta, date
from django.db.models import Sum 
from .models import AdminRevenueStatistics 

def admin_chart_processor(request):
    if request.path.startswith('/admin/') and request.user.is_authenticated:
        filter_type = request.GET.get('filter_type', 'all') 
        
        today = date.today()
        if filter_type == 'today':
            statistics = AdminRevenueStatistics.objects.filter(date=today)
        elif filter_type == 'yesterday':
            yesterday = today - timedelta(days=1)
            statistics = AdminRevenueStatistics.objects.filter(date=yesterday)
        elif filter_type == 'last_7_days':
            last_7_days = today - timedelta(days=7)
            statistics = AdminRevenueStatistics.objects.filter(date__gte=last_7_days)
        elif filter_type == 'custom_range':
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            if start_date and end_date:
                statistics = AdminRevenueStatistics.objects.filter(date__gte=start_date, date__lte=end_date)
            else:
                statistics = AdminRevenueStatistics.objects.none()
        else:
            statistics = AdminRevenueStatistics.objects.all()

        total_revenue = statistics.aggregate(total_revenue_sum=Sum('total_revenue'))['total_revenue_sum'] or 0
        publisher_revenue = statistics.aggregate(publisher_revenue_sum=Sum('publisher_revenue'))['publisher_revenue_sum'] or 0
        admin_revenue = statistics.aggregate(admin_revenue_sum=Sum('admin_revenue'))['admin_revenue_sum'] or 0
        total_impressions = statistics.aggregate(total_impressions_sum=Sum('total_impressions'))['total_impressions_sum'] or 0

        return {
            'total_revenue': total_revenue,
            'publisher_revenue': publisher_revenue,
            'admin_revenue': admin_revenue,
            'total_impressions': total_impressions,
            'statistics': statistics,
        }
    return {}
