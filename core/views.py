from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from .models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import timedelta
import requests
import geoip2.database
from django.db import transaction
from django.core.paginator import Paginator

from decimal import Decimal
from django.db.models import Sum, F
from datetime import date


# Create your views here.
# 23943b6bc3d4b6b68e10ea32ec72a3c4

def index(request):
    return render(request, 'index.html')

@login_required
def dashboard(request):
    placements = PublisherPlacement.objects.all()
    user_links = PlacementLink.objects.filter(user=request.user)
    generated_links = {link.placement_id: link.link for link in user_links}
    setting = Settings.objects.first()

    latest_notice = Notice.objects.filter(is_active=True).order_by('-created_at').first()
    notices = Notice.objects.filter(is_active=True).exclude(id=latest_notice.id).order_by('-created_at')

    paginator = Paginator(notices, 5) 
    page_number = request.GET.get('page')
    notices = paginator.get_page(page_number)

    grouped_statistics = ( AdStatistics.objects.filter(user=request.user).values('placement__title').annotate(
            total_impressions=Sum('impressions'),
            total_revenue=Sum('revenue')
        ).order_by('-total_revenue') 
    )
    statistics = AdStatistics.objects.filter(user=request.user).order_by('-id')

    chart_data = {
        "placements": [item["placement__title"] for item in grouped_statistics],
        "series": [
            {
                "name": "Impressions",
                "data": [item["total_impressions"] for item in grouped_statistics],
            },
            {
                "name": "Revenue",
                "data": [item["total_revenue"] for item in grouped_statistics],
            },
        ],
    }

    total_impressions = sum(item["total_impressions"] for item in grouped_statistics)

    total_revenue = sum(item["total_revenue"] for item in grouped_statistics)

    context = {
        'placements': placements,
        'generated_links': generated_links,
        'setting': setting,
        'latest_notice': latest_notice,
        'notices': notices,

        'grouped_statistics': grouped_statistics,
        'chart_data': chart_data,
        'total_impressions': total_impressions,
        'total_revenue' : total_revenue,
        'statistics' : statistics
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def notice_detail(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id, is_active=True)
    return render(request, 'notice_detail.html', {'notice': notice})

@login_required
def direct_link(request):
    placement_links = PlacementLink.objects.filter(user=request.user)
    
    context = {
        'placement_links' : placement_links,
    }
    return render(request, 'direct-link.html', context)

from collections import defaultdict
from django.db.models import Sum, F


@login_required
def statistics(request):
    grouped_statistics = (
        AdStatistics.objects.filter(user=request.user)
        .values('placement__title')
        .annotate(
            total_impressions=Sum('impressions'),
            total_revenue=Sum('revenue')
        )
        .order_by('-total_revenue') 
    )

    statistics = AdStatistics.objects.filter(user=request.user).order_by('-id')

    chart_data = {
        "placements": [item["placement__title"] for item in grouped_statistics],
        "series": [
            {
                "name": "Impressions",
                "data": [item["total_impressions"] for item in grouped_statistics],
            },
            {
                "name": "Revenue",
                "data": [item["total_revenue"] for item in grouped_statistics],
            },
        ],
    }

    total_impressions = sum(item["total_impressions"] for item in grouped_statistics)

    total_revenue = sum(item["total_revenue"] for item in grouped_statistics)

    return render(request, 'statistics.html', {
        'grouped_statistics': grouped_statistics,
        'chart_data': chart_data,
        'total_impressions': total_impressions,
        'total_revenue' : total_revenue,
        'statistics' : statistics
    })


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
def update_ad_statistics(placement_link, user):
    try:
        settings = Settings.objects.first()
        if not settings:
            print("Settings not found. Please configure your settings.")
            return

        api_key = settings.api_key
        start_date = "2024-10-10"
        finish_date = date.today().isoformat()

        api_url = (
            f"https://api3.adsterratools.com/publisher/stats.json"
            f"?placement={placement_link.placement.id}&start_date={start_date}&finish_date={finish_date}&group_by=placement"
        )
        headers = {'Accept': 'application/json', 'X-API-Key': api_key}
        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            print(f"API request failed with status code {response.status_code}: {response.text}")
            return

        data = response.json().get("items", [])
        if not data:
            print("No data returned from the API.")
            return

        total_revenue = sum(Decimal(item['revenue']) for item in data)
        admin_commission = Decimal(settings.commission)
        commission_amount = total_revenue * (admin_commission / 100)
        distributable_revenue = total_revenue - commission_amount

        ad_statistics = AdStatistics.objects.filter(placement_id=placement_link.placement.id)

        aggregated_stats = defaultdict(lambda: {"impressions": 0, "revenue": Decimal(0)})
        for stat in ad_statistics:
            key = stat.user.id
            aggregated_stats[key]["impressions"] += stat.impressions
            aggregated_stats[key]["revenue"] += stat.revenue

        total_impressions = sum(data["impressions"] for data in aggregated_stats.values())
        if total_impressions == 0:
            print("No impressions recorded for this placement. Revenue cannot be distributed.")
            return

        revenue_per_impression = distributable_revenue / total_impressions

        ad_stat, created = AdStatistics.objects.get_or_create(
            placement=placement_link.placement,
            date=date.today(),
            user=user,
            defaults={"revenue": Decimal(0), "impressions": 0},
        )
        ad_stat.revenue = F('revenue') + revenue_per_impression
        ad_stat.impressions = F('impressions') + 1
        ad_stat.save()

        print(f"Updated in DB: Revenue - {ad_stat.revenue}, Impressions - {ad_stat.impressions}")
        print(f"Successfully updated statistics for placement: {placement_link.placement.title}")

        return redirect(placement_link.direct_url)

    except Exception as e:
        print(f"{user.username}: {str(e)}")




def get_country_from_ip(ip_address):
    from django.conf import settings
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

    print(f"Visitor IP: {ip_address}, Country Code: {country_code}")

    if proxy is None and not is_duplicate_visitor(placement_link, ip_address):
        VisitorLog.objects.create(
            placement_link=placement_link,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return True

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
        update_ad_statistics(placement_link, user)
        return redirect(placement.direct_url)

    return JsonResponse({"message": "Disallowed user detected"}, status=403)
