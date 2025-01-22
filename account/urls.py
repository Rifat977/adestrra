from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path('login/', views.user_login, name="login"),
    path('forgot-password/', views.forgot_password, name="forgot_password"),
    path('new-password/<uidb64>/<token>/', views.new_password, name='new_password'),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register, name="register"),
    path('profile/', views.Profile, name="profile"),
    path('withdrawal/', views.request_withdrawal, name="request_withdrawal"),
]