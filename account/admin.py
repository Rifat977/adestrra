from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
from django.contrib import messages
from django.db.models import Sum
from core.models import PlacementLink, PublisherPlacement, AdStatistics
import requests

from django.contrib.admin import SimpleListFilter
from datetime import date, timedelta

admin.site.unregister(Group)

class DateFilterForUser(SimpleListFilter):
    title = 'Date Filter'
    parameter_name = 'custom_date_filter'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_year', 'This Year'),
            ('last_year', 'Last Year'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(date_joined=date.today())
        elif self.value() == 'yesterday':
            yesterday = date.today() - timedelta(days=1)
            return queryset.filter(date_joined=yesterday)
        elif self.value() == 'this_week':
            start_date = date.today() - timedelta(days=date.today().weekday())
            return queryset.filter(date_joined__gte=start_date)
        elif self.value() == 'last_week':
            start_date = date.today() - timedelta(days=7)
            end_date = start_date + timedelta(days=6)
            return queryset.filter(date_joined__gte=start_date, date_joined__lte=end_date)
        elif self.value() == 'this_month':
            start_date = date.today().replace(day=1)
            return queryset.filter(date_joined__gte=start_date)
        elif self.value() == 'last_month':
            first_day_this_month = date.today().replace(day=1)
            last_month_last_day = first_day_this_month - timedelta(days=1)
            start_date = last_month_last_day.replace(day=1)
            return queryset.filter(date_joined__gte=start_date, date_joined__lte=last_month_last_day)
        elif self.value() == 'this_year':
            start_date = date.today().replace(month=1, day=1)
            return queryset.filter(date_joined__gte=start_date)
        elif self.value() == 'last_year':
            start_date = date.today().replace(year=date.today().year - 1, month=1, day=1)
            end_date = start_date.replace(year=date.today().year) - timedelta(days=1)
            return queryset.filter(date_joined__gte=start_date, date_joined__lte=end_date)
        return queryset

Group._meta.verbose_name = "Permission"
Group._meta.verbose_name_plural = "Permissions"

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name",)  # Customize fields as needed



from django.contrib import admin
from .models import CustomUser

class CustomUserDisplay(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_approved', 'is_verified', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = (DateFilterForUser,)
    list_editable = ('is_approved',)
    
    actions = ['approve_users', 'reject_users']

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Admin').exists():
            return [field.name for field in self.model._meta.fields if field.name != 'is_approved'] + ['user_permissions', 'groups']
        return super().get_readonly_fields(request, obj)

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name='Admin').exists():
            return True
        return super().has_change_permission(request, obj)

    def approve_users(self, request, queryset):
        updated_count = queryset.update(is_approved='Active')
        self.message_user(request, f"{updated_count} user(s) successfully approved.")

    approve_users.short_description = "Approve selected users"

    def reject_users(self, request, queryset):
        updated_count = queryset.update(is_approved='Reject')  
        self.message_user(request, f"{updated_count} user(s) successfully rejected.")

    reject_users.short_description = "Reject selected users"

admin.site.register(CustomUser, CustomUserDisplay)


class DateFilterForWithdrawal(SimpleListFilter):
    title = 'Date Filter'
    parameter_name = 'custom_date_filter'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_year', 'This Year'),
            ('last_year', 'Last Year'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(requested_at=date.today())
        elif self.value() == 'yesterday':
            yesterday = date.today() - timedelta(days=1)
            return queryset.filter(requested_at=yesterday)
        elif self.value() == 'this_week':
            start_date = date.today() - timedelta(days=date.today().weekday())
            return queryset.filter(requested_at__gte=start_date)
        elif self.value() == 'last_week':
            start_date = date.today() - timedelta(days=7)
            end_date = start_date + timedelta(days=6)
            return queryset.filter(requested_at__gte=start_date, requested_at__lte=end_date)
        elif self.value() == 'this_month':
            start_date = date.today().replace(day=1)
            return queryset.filter(requested_at__gte=start_date)
        elif self.value() == 'last_month':
            first_day_this_month = date.today().replace(day=1)
            last_month_last_day = first_day_this_month - timedelta(days=1)
            start_date = last_month_last_day.replace(day=1)
            return queryset.filter(requested_at__gte=start_date, requested_at__lte=last_month_last_day)
        elif self.value() == 'this_year':
            start_date = date.today().replace(month=1, day=1)
            return queryset.filter(requested_at__gte=start_date)
        elif self.value() == 'last_year':
            start_date = date.today().replace(year=date.today().year - 1, month=1, day=1)
            end_date = start_date.replace(year=date.today().year) - timedelta(days=1)
            return queryset.filter(requested_at__gte=start_date, requested_at__lte=end_date)
        return queryset

@admin.register(UserBalanceWithdrawal)
class UserBalanceWithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'requested_at', 'processed_at', 'payment_method', 'account_number', 'admin_note')
    list_filter = (DateFilterForWithdrawal,)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('requested_at', 'processed_at')

    fields = ('user', 'amount', 'status', 'requested_at', 'processed_at', 'payment_method', 'account_number', 'account_details', 'admin_note')

    actions = ['approve_withdrawals', 'decline_withdrawals']

    def approve_withdrawals(self, request, queryset):
        print(f"Approving withdrawals: {queryset}")
        for withdrawal in queryset:
            try:
                withdrawal.approve(note="Approved by admin")
                self.message_user(request, f"Withdrawal {withdrawal.id} approved successfully.", level=messages.SUCCESS)
            except ValueError as e:
                self.message_user(request, f"Error approving withdrawal {withdrawal.id}: {e}", level=messages.ERROR)


    def decline_withdrawals(self, request, queryset):
        for withdrawal in queryset:
            try:
                withdrawal.decline(note="Declined by admin.")
                self.message_user(request, f"Withdrawal {withdrawal.id} declined successfully.", level=messages.SUCCESS)
            except ValueError as e:
                self.message_user(request, f"Error declining withdrawal {withdrawal.id}: {e}", level=messages.ERROR)

    approve_withdrawals.short_description = "Approve selected withdrawals"
    decline_withdrawals.short_description = "Decline selected withdrawals"


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('domain', 'api_key', 'email', 'skype', 'commission')
    search_fields = ('domain', 'api_key',)

    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


from decimal import Decimal
from datetime import date
from django.db.models import Sum

class DateFilter(SimpleListFilter):
    title = 'Date Filter'
    parameter_name = 'custom_date_filter'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_year', 'This Year'),
            ('last_year', 'Last Year'),
        )
    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(date=date.today())
        elif self.value() == 'yesterday':
            yesterday = date.today() - timedelta(days=1)
            return queryset.filter(date=yesterday)
        elif self.value() == 'this_week':
            start_date = date.today() - timedelta(days=date.today().weekday())
            return queryset.filter(date__gte=start_date)
        elif self.value() == 'last_week':
            start_date = date.today() - timedelta(days=7)
            return queryset.filter(date__gte=start_date)
        elif self.value() == 'this_month':
            start_date = date.today().replace(day=1)
            return queryset.filter(date__gte=start_date)
        elif self.value() == 'last_month':
            start_date = date.today() - timedelta(days=30)
            return queryset.filter(date__gte=start_date)
        elif self.value() == 'this_year':
            start_date = date.today().replace(month=1, day=1)
            return queryset.filter(date__gte=start_date)
        elif self.value() == 'last_year':
            start_date = date.today().replace(year=date.today().year - 1, month=1, day=1)
            return queryset.filter(date__gte=start_date)

@admin.register(AdminRevenueStatistics)
class AdminRevenueStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_revenue', 'publisher_revenue', 'admin_revenue', 'total_impressions')
    list_filter = (DateFilter,)
    # search_fields = ('date',)

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def get_queryset(self, request):
    #     self.update_statistics_for_all_placements(request)
    #     return super().get_queryset(request)

    # def update_statistics_for_all_placements(self, request):
    #     settings = Settings.objects.first()
    #     if not settings:
    #         self.message_user(request, "Settings not found. Please configure your settings.", level="error")
    #         return

    #     api_key = settings.api_key
    #     start_date = "2024-10-10"
    #     finish_date = date.today().isoformat()

    #     total_revenue = Decimal(0)
    #     total_impressions = 0

    #     placement_links = PlacementLink.objects.all()
    #     if not placement_links.exists():
    #         # self.message_user(request, "No placement links found.", level="warning")
    #         return

    #     for placement_link in placement_links:
    #         api_url = (
    #             f"https://api3.adsterratools.com/publisher/stats.json"
    #             f"?placement={placement_link.placement.id}&start_date={start_date}&finish_date={finish_date}&group_by=placement"
    #         )
    #         headers = {'Accept': 'application/json', 'X-API-Key': api_key}

    #         try:
    #             response = requests.get(api_url, headers=headers)
    #             if response.status_code != 200:
    #                 self.message_user(
    #                     request,
    #                     f"API request failed for placement {placement_link.placement.title} "
    #                     f"with status code {response.status_code}: {response.text}",
    #                     level="error",
    #                 )
    #                 continue

    #             data = response.json().get("items", [])
    #             if not data:
    #                 self.message_user(
    #                     request,
    #                     f"No data returned from the API for placement {placement_link.placement.title}.",
    #                     level="warning",
    #                 )
    #                 continue

    #             placement_revenue = sum(Decimal(item['revenue']) for item in data)
    #             total_revenue += placement_revenue

    #         except requests.RequestException as e:
    #             self.message_user(
    #                 request,
    #                 f"API request failed for placement {placement_link.placement.title}: {str(e)}",
    #                 level="error",
    #             )
    #         except Exception as e:
    #             self.message_user(
    #                 request,
    #                 f"An unexpected error occurred for placement {placement_link.placement.title}: {str(e)}",
    #                 level="error",
    #             )

    #     total_impressions = AdStatistics.objects.aggregate(Sum('impressions'))['impressions__sum'] or 0

    #     admin_commission = Decimal(settings.commission) / 100
    #     admin_revenue = total_revenue * admin_commission
    #     publisher_revenue = total_revenue - admin_revenue

    #     AdminRevenueStatistics.objects.update_or_create(
    #         defaults={
    #             'total_revenue': total_revenue,
    #             'publisher_revenue': publisher_revenue,
    #             'admin_revenue': admin_revenue,
    #             'total_impressions': total_impressions,
    #         },
    #     )

    #     self.message_user(request, "Statistics successfully updated for all placements.", level="success")
