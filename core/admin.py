from django.contrib import admin
import requests
from .models import *
from django.utils.timezone import now

from django.utils.safestring import mark_safe

@admin.register(PublisherPlacement)
class PublisherPlacementAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain_id', 'title', 'alias', 'is_active')
    search_fields = ('title', 'alias', 'domain_id', 'is_active')
    list_filter = ('title', 'domain_id', 'is_active',)
    
    api_fetched = False 

    def get_queryset(self, request):
        if not PublisherPlacementAdmin.api_fetched:
            self.fetch_publisher_placements()
            PublisherPlacementAdmin.api_fetched = True
        return super().get_queryset(request)

    def fetch_publisher_placements(self):
        settings = Settings.objects.first()

        api_key = settings.api_key

        api_url = "https://api3.adsterratools.com/publisher/placements.json"
        headers = {
            'Accept': 'application/json',
            'X-API-Key': api_key,
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            data = response.json().get("items", [])
            for item in data:
                obj, created = PublisherPlacement.objects.update_or_create(
                    id=item["id"],
                    defaults={
                        "domain_id": item["domain_id"],
                        "alias": item.get("alias", ""),
                        "direct_url": item.get("direct_url", ""),
                    },
                )
                if created:
                    obj.title = item["title"]
                    obj.save()
            print(f"Fetched {len(data)} publisher placements successfully.")
        else:
            print(
                f"Failed to fetch publisher placements. Status code: {response.status_code}"
            )

    # def has_add_permission(self, request):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False


from django.contrib.admin import SimpleListFilter
from datetime import date, timedelta

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
        return queryset

class AdStatisticsAdmin(admin.ModelAdmin):
    list_display = ('placement', 'user', 'date', 'impressions', 'revenue', 'subid')
    search_fields = ('placement__title', 'user__username', 'date')
    list_filter = (DateFilter,)

class PlacementLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'placement', 'subid', 'link')
    search_fields = ('user__username', 'placement__title')

    # def has_add_permission(self, request):
    #     return False



class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('placement_link', 'ip_address', 'user_agent', 'visited_at')
    search_fields = ('placement_link', 'ip_address', 'user_agent', 'visited_at')


admin.site.register(AdStatistics, AdStatisticsAdmin)
admin.site.register(PlacementLink, PlacementLinkAdmin)
# admin.site.register(VisitorLog, VisitorLogAdmin)
admin.site.register(Notice)
admin.site.register(SubID)
