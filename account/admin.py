from django.contrib import admin
from django.contrib.auth.models import Group
from .models import CustomUser

admin.site.unregister(Group)

class CustomUserDisplay(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_verified', 'is_approved', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_verified', 'is_approved', ('date_joined', admin.DateFieldListFilter))


admin.site.register(CustomUser, CustomUserDisplay)