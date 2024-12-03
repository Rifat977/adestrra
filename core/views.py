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
from django.db import transaction
from django.db.models import F



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


@transaction.atomic
def update_ad_statistics(placement_link, country_code, user):
    try:
        country_revenue = CountryRevenue.objects.filter(country=country_code).first()
        total_revenue = country_revenue.revenue if country_revenue else 0.0
        print(total_revenue)

        if not placement_link:
            print(f"User {user.username} is not linked to placement {placement_link.placement.title}. No updates made.")
            return

        ad_stat, created = AdStatistics.objects.get_or_create(
            placement=placement_link.placement,
            user=user,
            defaults={"revenue": 0.0, "impressions": 0},
        )

        ad_stat.revenue = F('revenue') + total_revenue
        ad_stat.impressions += 1
        ad_stat.save()

        updated_stat = AdStatistics.objects.get(id=ad_stat.id)
        print(f"Updated in DB: Revenue - {updated_stat.revenue}, Impressions - {updated_stat.impressions}")
        print(f"Successfully updated statistics for placement: {placement_link.placement.title} | Country: {country_code}")

        
        return redirect(placement_link.direct_url)

    except Exception as e:
        print(f"Error updating revenue for user {user.username}: {str(e)}")



def get_country_from_ip(ip_address):
    geoip_db_path = settings.BASE_DIR / 'GeoLite2-Country.mmdb'
    try:
        with geoip2.database.Reader(str(geoip_db_path)) as reader:
            response = reader.country(ip_address)
            return response.country.iso_code
    except geoip2.errors.AddressNotFoundError:
        return None
    except Exception as e:
        print(f"Error in IP geolocation: {str(e)}")
        return None


def is_duplicate_visitor(placement_link, ip_address):
    return VisitorLog.objects.filter(
        placement_link=placement_link,
        ip_address=ip_address,
    ).exists()


def track_visit(request, placement_link, user):
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    proxy = request.META.get('HTTP_VIA', None)
    user_agent = request.META.get('HTTP_USER_AGENT', None)

    country_code = get_country_from_ip(ip_address)
    # country_code = 'BD'

    print(f"Visitor IP: {ip_address}, Country Code: {country_code}")

    if proxy is None and country_code and not is_duplicate_visitor(placement_link, ip_address):
        VisitorLog.objects.create(
            placement_link=placement_link,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return country_code

    print(f"Invalid or duplicate visit detected: IP {ip_address}, Proxy: {proxy}")
    return False


def redirect_to_ad(request, placement_id, unique_id):
    placement_link = get_object_or_404(
        PlacementLink, placement_id=placement_id, link__contains=unique_id
    )
    placement = placement_link.placement
    user = placement_link.user

    track_visit_result = track_visit(request, placement_link, user)

    if track_visit_result:
        update_ad_statistics(placement_link, track_visit_result, user)
        return redirect(placement.direct_url)

    return JsonResponse({"message": "Disallowed user detected"}, status=403)
