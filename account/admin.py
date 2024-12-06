from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
from django.contrib import messages


admin.site.unregister(Group)

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
    list_display = ('user', 'amount', 'status', 'requested_at', 'processed_at', 'account_number', 'admin_note')
    list_filter = ('status', 'requested_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('requested_at', 'processed_at')

    fields = ('user', 'amount', 'status', 'requested_at', 'processed_at', 'account_number', 'account_details', 'admin_note')

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
