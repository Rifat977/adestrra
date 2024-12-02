from django.contrib import admin
import requests
from .models import *
from django.utils.timezone import now
from django.conf import settings

@admin.register(PublisherPlacement)
class PublisherPlacementAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain_id', 'title', 'alias', 'direct_url')
    search_fields = ('title', 'alias', 'domain_id')
    
    
    def get_queryset(self, request):
        self.fetch_publisher_placements()
        return super().get_queryset(request)

    def fetch_publisher_placements(self):
        api_url = "https://api3.adsterratools.com/publisher/placements.json"
        headers = {
            'Accept': 'application/json',
            'X-API-Key': settings.API_KEY,
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            data = response.json().get("items", [])
            for item in data:
                PublisherPlacement.objects.update_or_create(
                    id=item["id"],
                    defaults={
                        "domain_id": item["domain_id"],
                        "title": item["title"],
                        "alias": item.get("alias", ""),
                        "direct_url": item.get("direct_url", ""),
                    },
                )
            print(f"Fetched {len(data)} publisher placements successfully.")
        else:
            print(f"Failed to fetch publisher placements. Status code: {response.status_code}",
                level="error",
            )

    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class AdStatisticsAdmin(admin.ModelAdmin):
    list_display = ('placement', 'user', 'date', 'impressions', 'revenue')
    search_fields = ('placement__title', 'user__username', 'date')
    list_filter = ('placement', 'date', 'user')

class PlacementLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'placement', 'link')
    search_fields = ('user__username', 'placement__title')

class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('placement_link', 'ip_address', 'user_agent', 'visited_at')
    search_fields = ('placement_link', 'ip_address', 'user_agent', 'visited_at')


admin.site.register(AdStatistics, AdStatisticsAdmin)
admin.site.register(PlacementLink, PlacementLinkAdmin)
admin.site.register(CountryRevenue)
admin.site.register(VisitorLog, VisitorLogAdmin)
