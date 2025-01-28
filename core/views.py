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

from account.models import AdminRevenueStatistics

import json
from decimal import Decimal

import datetime
import random

from account.models import CustomUser


# Create your views here.
# 23943b6bc3d4b6b68e10ea32ec72a3c4

def index(request):
    return render(request, 'landing/index.html')

def contact(request):
    setting = Settings.objects.first()
    context = {
        'setting' : setting
    }
    return render(request, 'landing/contact-us.html', context)

def privacy(request):

    return render(request, 'landing/privacy.html')

import decimal

def custom_dashboard(request):
    return render(request, 'admin/base_site.html', {})

# Helper function to convert Decimal to float
def decimal_to_float(value):
    if isinstance(value, decimal.Decimal):
        return float(value)
    return value

@login_required
def dashboard(request):
    placements = PublisherPlacement.objects.all()
    user_links = PlacementLink.objects.filter(user=request.user)
    generated_links = {link.placement_id: link.link for link in user_links}

    latest_notice = Notice.objects.filter(is_active=True).order_by('-created_at').first()
    notices = Notice.objects.filter(is_active=True)
    if latest_notice:
        notices = notices.exclude(id=latest_notice.id)
    notices = notices.order_by('-created_at')

    paginator = Paginator(notices, 5) 
    page_number = request.GET.get('page')
    notices = paginator.get_page(page_number)

    grouped_statistics = AdStatistics.objects.filter(user=request.user).values(
        'placement__title'
    ).annotate(
        total_impressions=Sum('impressions'),
        total_revenue=Sum('revenue')
    ).order_by('-total_revenue')

    if not grouped_statistics.exists():
        grouped_statistics = []

    statistics = AdStatistics.objects.filter(user=request.user).order_by('-id')

    today = datetime.date.today()

    weekly_labels = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    monthly_labels = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]

    weekly_labels_reversed = weekly_labels[::-1]
    monthly_labels_reversed = monthly_labels[::-1]

    print(weekly_labels_reversed)
    print(monthly_labels_reversed)

    monthly_impressions = []
    monthly_revenue = []
    for i in range(30):
        date = today - datetime.timedelta(days=i)
        daily_stats = AdStatistics.objects.filter(user=request.user, date=date).aggregate(
            total_impressions=Sum('impressions'),
            total_revenue=Sum('revenue')
        )
        monthly_impressions.append(daily_stats['total_impressions'] or 0)
        monthly_revenue.append(daily_stats['total_revenue'] or 0)

    chart_data = {
        "placements": [item["placement__title"] for item in grouped_statistics],
        "series": [
            {
                "name": "Impressions",
                "data": [int(item.get("total_impressions", 0) or 0) for item in grouped_statistics],
            },
            {
                "name": "Revenue",
                "data": [decimal_to_float(item.get("total_revenue", 0) or 0) for item in grouped_statistics],
            },
        ],
    }

    weekly_impressions = []
    weekly_revenue = []
    for date in weekly_labels_reversed:
        daily_stats = AdStatistics.objects.filter(
            user=request.user,
            date=date
        ).aggregate(
            total_impressions=Sum('impressions'),
            total_revenue=Sum('revenue')
        )
        weekly_impressions.append(daily_stats['total_impressions'] or 0)
        weekly_revenue.append(daily_stats['total_revenue'] or 0)



    chart_data_2 = {
        "weekly_labels": weekly_labels_reversed,
        "monthly_labels": monthly_labels_reversed,
        "weekly_series": [
            {
                "name": "Impressions",
                "data": weekly_impressions,
            },
            {
                "name": "Revenue",
                "data": weekly_revenue,
            },
        ],
        "monthly_series": [
            {
                "name": "Impressions",
                "data": monthly_impressions,
            },
            {
                "name": "Revenue",
                "data": monthly_revenue,
            },
        ],
    }

    total_impressions = sum(int(item.get("total_impressions", 0) or 0) for item in grouped_statistics)
    total_revenue = sum(decimal_to_float(item.get("total_revenue", 0) or 0) for item in grouped_statistics)

    chart_data_2_serializable = {
        "weekly_labels": weekly_labels_reversed,
        "monthly_labels": monthly_labels_reversed,
        "weekly_series": [
            {
                "name": "Impressions",
                "data": weekly_impressions,
            },
            {
                "name": "Revenue",
                "data": [decimal_to_float(revenue) for revenue in weekly_revenue],
            },
        ],
        "monthly_series": [
            {
                "name": "Impressions",
                "data": [decimal_to_float(impression) for impression in monthly_impressions],
            },
            {
                "name": "Revenue",
                "data": [decimal_to_float(revenue) for revenue in monthly_revenue],
            },
        ],
    }

    placement_statistics = (
        AdStatistics.objects.filter(user=request.user)
        .values('placement__title')  
        .annotate(
            total_impressions=Sum('impressions'),
            total_revenue=Sum('revenue')
        )
        .order_by('-total_impressions') 
    )

    subid_statistics = (
        AdStatistics.objects.filter(user=request.user)
        .values('subid__name')  
        .annotate(
            total_impressions=Sum('impressions'),
            total_revenue=Sum('revenue')
        )
        .order_by('-total_impressions') 
    )


    context = {
        'placements': placements,
        'generated_links': generated_links,
        'latest_notice': latest_notice,
        'notices': notices,
        'grouped_statistics': grouped_statistics,
        'chart_data': chart_data,
        'total_impressions': total_impressions,
        'total_revenue': total_revenue,
        'statistics': statistics,
        'chart_data_2': json.dumps(chart_data_2_serializable),
        'placement_statistics': placement_statistics,
        'subid_statistics' : subid_statistics
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def notice_detail(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id, is_active=True)
    return render(request, 'notice_detail.html', {'notice': notice})

@login_required
def direct_link(request):
    user_links = PlacementLink.objects.filter(user=request.user)
    generated_links = {
        link.placement_id: {
            'link': link.link,
            'used_subids': list(
                PlacementLink.objects.filter(user=request.user, placement=link.placement)
                .values_list('subid_id', flat=True)
            )
        }
        for link in user_links
    }
    context = {
        'placement_links': user_links,
        'placements': PublisherPlacement.objects.filter(is_active=True),
        'generated_links': generated_links,
        'subids': SubID.objects.all(),
    }
    return render(request, 'direct-link.html', context)


from collections import defaultdict
from django.db.models import F
from django.core.paginator import Paginator
from django.db.models import Sum, Subquery, OuterRef


@login_required
def statistics(request):

    from datetime import datetime


    # Get the date range from the request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Convert string dates to datetime objects
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        start_date = end_date = None

    # Filter AdStatistics based on the date range
    statistics_list = AdStatistics.objects.filter(user=request.user)
    if start_date:
        statistics_list = statistics_list.filter(date__gte=start_date)
    if end_date:
        statistics_list = statistics_list.filter(date__lte=end_date)

    # Annotate subid_name
    statistics_list = statistics_list.select_related('placement').annotate(
        subid_name=Subquery(
            PlacementLink.objects.filter(
                placement=OuterRef('placement'),
                user=OuterRef('user')
            ).values('subid__name')[:1]
        )
    ).order_by('-id')

    # Grouped statistics for chart
    grouped_statistics = (
        statistics_list.values('placement__title')
        .annotate(
            total_impressions=Sum('impressions'),
            total_revenue=Sum('revenue')
        )
        .order_by('-total_revenue')
    )

    # Add pagination
    paginator = Paginator(statistics_list, 10)  # Show 10 items per page
    page = request.GET.get('page')
    statistics = paginator.get_page(page)

    # Chart data
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
        'total_revenue': total_revenue,
        'statistics': statistics,
    })


@login_required
def generate_link(request):
    if request.method == "POST":
        custom_user = CustomUser.objects.get(username=request.user)
        if custom_user.is_approved == "Active":
            placement_id = request.POST.get("placement_id")
            sub_id = request.POST.get("subid")
            subid = SubID.objects.get(id=int(sub_id))
            if not placement_id:
                return JsonResponse({"error": "Placement ID is required."}, status=400)

            try:
                placement = PublisherPlacement.objects.get(id=placement_id)
            except PublisherPlacement.DoesNotExist:
                return JsonResponse({"error": "Placement not found."}, status=404)

            placement_link, created = PlacementLink.objects.get_or_create(
                user=request.user,
                subid=subid,
                placement=placement
            )

            return JsonResponse({
                "link": placement_link.link,
                "created": created  
            })
        else:
            return JsonResponse({
                "link" : "",
                "created": ""  
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
        print(data)
        for item in data:
            cpm = Decimal(item.get('cpm', 0))  # Safely get 'cpm' from the dictionary
            revenue_per_impression = cpm / 1000
            print('revenue_per_impression', revenue_per_impression)

            admin_commission = Decimal(settings.commission)
            commission_amount = revenue_per_impression * (admin_commission / 100)
            print('admin commission', commission_amount)

            publisher_revenue_per_impression = revenue_per_impression - commission_amount
            print('after tax publisher_revenue_per_impression', publisher_revenue_per_impression)

            ad_stat, created = AdStatistics.objects.get_or_create(
                placement=placement_link.placement,
                date=date.today(),
                user=user,
                subid=placement_link.subid,
                defaults={"revenue": Decimal(0), "impressions": 0},
            )
            ad_stat.revenue = F('revenue') + revenue_per_impression
            ad_stat.impressions = F('impressions') + 1
            ad_stat.save()

            print(f"Updated in DB: Revenue - {ad_stat.revenue}, Impressions - {ad_stat.impressions}")

            admin_stats, created = AdminRevenueStatistics.objects.get_or_create(
                date=date.today(),
                defaults={
                    "total_revenue": Decimal(0),
                    "publisher_revenue": Decimal(0),
                    "admin_revenue": Decimal(0),
                    "total_impressions": 0,
                },
            )
            admin_stats.total_revenue = F('total_revenue') + revenue_per_impression
            admin_stats.publisher_revenue = F('publisher_revenue') + publisher_revenue_per_impression
            admin_stats.admin_revenue = F('admin_revenue') + commission_amount
            admin_stats.total_impressions = F('total_impressions') + 1
            admin_stats.save()

            print(f"Admin stats updated: Total Revenue - {admin_stats.total_revenue}, "
                  f"Publisher Revenue - {admin_stats.publisher_revenue}, "
                  f"Admin Revenue - {admin_stats.admin_revenue}, "
                  f"Total Impressions - {admin_stats.total_impressions}")

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
    return True

    print(f"Invalid or duplicate visit detected: IP {ip_address}, Proxy: {proxy}")
    return False


def redirect_to_ad(request, placement_id, unique_id, subid):
    placement_link = get_object_or_404(
        PlacementLink, placement_id=placement_id, link__contains=str(unique_id)
    )
    placement = placement_link.placement
    user = placement_link.user

    track_visit_result = track_visit(request, placement_link, user)

    if track_visit_result:
        update_ad_statistics(placement_link, user)
        return redirect(placement.direct_url)

    return JsonResponse({"message": "Disallowed user detected"}, status=403)

