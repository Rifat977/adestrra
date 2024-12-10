from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
from django.contrib import messages
from django.db.models import Sum
from core.models import PlacementLink, PublisherPlacement, AdStatistics
import requests


# admin.site.unregister(Group)

class CustomUserDisplay(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_verified', 'is_approved', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_verified', 'is_approved', ('date_joined', admin.DateFieldListFilter))
    list_editable = ('is_approved',)  
    
    actions = ['approve_users', 'disapprove_users']

    def approve_users(self, request, queryset):
        updated_count = queryset.update(is_approved=True)
        self.message_user(request, f"{updated_count} user(s) successfully approved.")

    approve_users.short_description = "Approve selected users"

    def disapprove_users(self, request, queryset):
        updated_count = queryset.update(is_approved=False)
        self.message_user(request, f"{updated_count} user(s) successfully disapproved.")

    disapprove_users.short_description = "Disapprove selected users"

admin.site.register(CustomUser, CustomUserDisplay)


@admin.register(UserBalanceWithdrawal)
class UserBalanceWithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'requested_at', 'processed_at', 'payment_method', 'account_number', 'admin_note')
    list_filter = ('status', 'requested_at')
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

@admin.register(AdminRevenueStatistics)
class AdminRevenueStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_revenue', 'publisher_revenue', 'admin_revenue', 'total_impressions')
    list_filter = ('date',)

    def get_queryset(self, request):
        self.update_statistics_for_all_placements(request)
        return super().get_queryset(request)

    def update_statistics_for_all_placements(self, request):
        settings = Settings.objects.first()
        if not settings:
            self.message_user(request, "Settings not found. Please configure your settings.", level="error")
            return

        api_key = settings.api_key
        start_date = "2024-10-10"
        finish_date = date.today().isoformat()

        total_revenue = Decimal(0)
        total_impressions = 0

        placement_links = PlacementLink.objects.all()
        if not placement_links.exists():
            self.message_user(request, "No placement links found. Please ensure placements are configured.", level="error")
            return

        for placement_link in placement_links:
            api_url = (
                f"https://api3.adsterratools.com/publisher/stats.json"
                f"?placement={placement_link.placement.id}&start_date={start_date}&finish_date={finish_date}&group_by=placement"
            )
            headers = {'Accept': 'application/json', 'X-API-Key': api_key}

            try:
                response = requests.get(api_url, headers=headers)
                if response.status_code != 200:
                    self.message_user(
                        request,
                        f"API request failed for placement {placement_link.placement.title} "
                        f"with status code {response.status_code}: {response.text}",
                        level="error",
                    )
                    continue

                data = response.json().get("items", [])
                if not data:
                    self.message_user(
                        request,
                        f"No data returned from the API for placement {placement_link.placement.title}.",
                        level="warning",
                    )
                    continue

                placement_revenue = sum(Decimal(item['revenue']) for item in data)
                total_revenue += placement_revenue

            except requests.RequestException as e:
                self.message_user(
                    request,
                    f"API request failed for placement {placement_link.placement.title}: {str(e)}",
                    level="error",
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"An unexpected error occurred for placement {placement_link.placement.title}: {str(e)}",
                    level="error",
                )

        total_impressions = AdStatistics.objects.aggregate(Sum('impressions'))['impressions__sum'] or 0

        admin_commission = Decimal(settings.commission) / 100
        admin_revenue = total_revenue * admin_commission
        publisher_revenue = total_revenue - admin_revenue

        AdminRevenueStatistics.objects.update_or_create(
            date=date.today(),
            defaults={
                'total_revenue': total_revenue,
                'publisher_revenue': publisher_revenue,
                'admin_revenue': admin_revenue,
                'total_impressions': total_impressions,
            },
        )

        self.message_user(request, "Statistics successfully updated for all placements.", level="success")
