from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login

# Create your views here.
def register(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'account/register.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'account/login.html')