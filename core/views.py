from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from .models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from datetime import timedelta
import requests
import geoip2.database


# Create your views here.
# 23943b6bc3d4b6b68e10ea32ec72a3c4

@login_required
def dashboard(request):
    placements = PublisherPlacement.objects.all()
    user_links = PlacementLink.objects.filter(user=request.user)
    generated_links = {link.placement_id: link.link for link in user_links}

    context = {
        'placements': placements,
        'generated_links': generated_links,
    }
    return render(request, 'dashboard.html', context)

@login_required
def direct_link(request):
    placement_links = PlacementLink.objects.filter(user=request.user)
    
    context = {
        'placement_links' : placement_links,
    }
    return render(request, 'direct-link.html', context)


@login_required
def statistics(request):
    statistics = AdStatistics.objects.filter(user=request.user)
    context = {
        'statistics' : statistics
    }
    return render(request, 'statistics.html', context)


@login_required
def generate_link(request):
    if request.method == "POST":
        placement_id = request.POST.get("placement_id")
        if not placement_id:
            return JsonResponse({"error": "Placement ID is required."}, status=400)

        try:
            placement = PublisherPlacement.objects.get(id=placement_id)
        except PublisherPlacement.DoesNotExist:
            return JsonResponse({"error": "Placement not found."}, status=404)

        placement_link, created = PlacementLink.objects.get_or_create(
            user=request.user,
            placement=placement
        )

        return JsonResponse({
            "link": placement_link.link,
            "created": created  
        })

    return JsonResponse({"error": "Invalid request method."}, status=405)


def update_ad_statistics(placement, country_code):
    try:
        country_revenue = CountryRevenue.objects.filter(country=country_code).aggregate(
            total_revenue=models.Sum('revenue'),
            total_impressions=models.Sum('impressions')
        )

        total_revenue = country_revenue['total_revenue'] or 0.0
        total_impressions = country_revenue['total_impressions'] or 0

        linked_users = PlacementLink.objects.filter(placement=placement).select_related('user')

        for link in linked_users:
            user = link.user

            user_revenue = total_revenue / len(linked_users) if linked_users else 0
            user_impressions = total_impressions / len(linked_users) if linked_users else 0

            ad_stat, created = AdStatistics.objects.update_or_create(
                placement=placement,
                user=user,
                defaults={
                    "revenue": user_revenue,
                    "impressions": user_impressions,
                }
            )

            print(f"Updated stats for {user.username}: Revenue - {user_revenue}, Impressions - {user_impressions}")

        print(f"Successfully updated statistics for placement: {placement.title} | Country: {country_code}")

    except Exception as e:
        print(f"Error updating statistics: {e}")


from datetime import timedelta

def get_country_from_ip(ip_address):
    geoip_db_path = settings.BASE_DIR / 'GeoLite2-Country.mmdb'
    try:
        with geoip2.database.Reader(geoip_db_path) as reader:
            response = reader.country(ip_address)
            return response.country.iso_code  
    except geoip2.errors.AddressNotFoundError:
        return None


def is_duplicate_visitor(placement_link, ip_address):
    recent_logs = VisitorLog.objects.filter(
        placement_link=placement_link,
        ip_address=ip_address
    )
    return recent_logs.exists()

def track_visit(request, placement_link):
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    proxy = request.META.get('HTTP_VIA', None) 
    user_agent = request.META.get('HTTP_USER_AGENT', None)
    country_code = get_country_from_ip(ip_address)

    print(country_code)
    
    if proxy is None and country_code and not is_duplicate_visitor(placement_link, ip_address):
        VisitorLog.objects.create(
            placement_link=placement_link,
            ip_address=ip_address,
            user_agent=user_agent
        )
        update_ad_statistics(placement, country_code)
        return True 
    return False  


def redirect_to_ad(request, placement_id, unique_id):
    placement_link = get_object_or_404(PlacementLink, placement_id=placement_id, link__contains=unique_id)
    placement = placement_link.placement
    user = request.user
    today = timezone.now().date()

    ad_stat, created = AdStatistics.objects.get_or_create(
        placement=placement,
        user=user,
        date=today,
    )

    track_visit_result = track_visit(request, placement_link)

    if track_visit_result:
        if created:
            ad_stat.impressions = 1
        else:
            ad_stat.impressions += 1

        ad_stat.save()
        
        return redirect(placement.direct_url)
    else:
        return JsonResponse({
            "message": "Disallowed user detected",
        })

