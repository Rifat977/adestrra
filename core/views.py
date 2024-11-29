from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from .models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from datetime import timedelta
import requests

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


def update_ad_statistics(placement):
        finish_date = timezone.now().date()
        start_date = finish_date - timedelta(days=7)

        api_url = "https://api3.adsterratools.com/publisher/stats.json"
        headers = {
            'Accept': 'application/json',
            'X-API-Key': '23943b6bc3d4b6b68e10ea32ec72a3c4',
        }
        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "finish_date": finish_date.strftime('%Y-%m-%d'),
            "group_by": "placement",  
            "placement": placement.id, 
        }

        response = requests.get(api_url, headers=headers, params=params)


        if response.status_code == 200:
            data = response.json().get("items", [])
            linked_users = PlacementLink.objects.filter(placement=placement).select_related('user')

            data = data[0]

            for link in linked_users:
                user = link.user

                ad_stat, created = AdStatistics.objects.update_or_create(
                    placement=placement,
                    user=user,
                    defaults={
                        "impressions": data['impression'],
                        "clicks": data['clicks'],
                        "ctr": data['ctr'],
                        "cpm": data['cpm'],
                        "revenue": data['revenue'],
                    }
                )
            print(f"Successfully updated statistics for placement: {placement.title}")
        else:
            print(f"Failed to fetch statistics. Status code: {response.status_code}")



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

    update_ad_statistics(placement)

    # if created:
    #     ad_stat.impressions = 1
    # else:
    #     ad_stat.impressions += 1

    # ad_stat.save()

    return redirect(placement.direct_url)
