from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.index, name="index"),
    path('redirect/<int:placement_id>/<uuid:unique_id>/', views.redirect_to_ad, name='redirect_to_ad'),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('links/', views.direct_link, name="direct_link"),
    path('statistics/', views.statistics, name="statistics"),
    path('generate-link/', views.generate_link, name='generate_link'),

    path('notice/<int:notice_id>/', views.notice_detail, name='notice_detail'),
]