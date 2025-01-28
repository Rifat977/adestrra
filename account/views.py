from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.utils.timezone import now
from .models import *
from decimal import Decimal

from django.utils.html import strip_tags
from django.template.loader import render_to_string
from . import send_email

from django.utils.crypto import get_random_string, constant_time_compare
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse



# Create your views here.
def register(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()

            if not username or not email or not password:
                messages.error(request, "All fields are required.")
                return render(request, 'account/register.html')

            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken.")
                return render(request, 'account/register.html')

            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered.")
                return render(request, 'account/register.html')

            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_verified=True,
                balance=0.0,
                email_verification_token=get_random_string(50),
                email_verification_sent_at=now(),
            )

            user.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Registration successful!")
            return redirect('core:dashboard')
        else:
            return render(request, 'account/register.html')

def verify_email(request, token):
    user = CustomUser.objects.filter(email_verification_token=token).first()
    if user:
        user.is_verified = True
        user.email_verification_token = None
        user.save()
        messages.success(request, "Email verified successfully!")
        return redirect('account:login')
    else:
        messages.error(request, "Invalid or expired verification link.")
        return redirect('account:register')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('account:login') 



def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, username=email, password=password)

            if user:
                if user.is_verified:
                    login(request, user)
                    print(f"Debug: User logged in - {user.username}")  
                    messages.success(request, "Login successful!")
                    return redirect('core:dashboard')
                else:
                    print(f"Debug: User not verified or approved - {user.username}") 
                    messages.error(request, "Your account is not verified or approved.")
            else:
                print("Debug: Invalid email or password.") 
                messages.error(request, "Invalid email or password.")
                
        return render(request, 'account/login.html')




@login_required
def request_withdrawal(request):
    withdrawals = UserBalanceWithdrawal.objects.filter(user=request.user)

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0.0))
        account_number = request.POST.get('account_number', '').strip()
        account_details = request.POST.get('account_details', '').strip()
        payment_method = request.POST.get('payment_method', '').strip()

        if amount <= 0:
            messages.error(request, "Invalid withdrawal amount.")
        elif amount > request.user.balance:
            messages.error(request, "Insufficient balance.")
        elif not account_number or not account_details:
            messages.error(request, "Account number and account details are required.")
        else:
            UserBalanceWithdrawal.objects.create(
                user=request.user,
                amount=amount,
                payment_method=payment_method,
                account_number=account_number,
                account_details=account_details
            )
            messages.success(request, "Withdrawal request submitted successfully.")
            return redirect('account:request_withdrawal')

    return render(request, 'withdrawal_form.html', {
        'withdrawals': withdrawals
    })

def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:  
            messages.error(request, 'No user found with that email address.')
            return redirect('account:forgot_password')

        if user is not None:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = reset_url = request.build_absolute_uri(f"/accounts/new-password/{uid}/{token}/")

            subject = f"Password Reset Request"
            html_content = render_to_string('email/password-reset.html', {
                'user': user,
                'reset_link': reset_link,
            })
            text_content = strip_tags(html_content)
            send_mail(subject, text_content, 'noreply@cparobust.com', [user.email], html_message=html_content)

            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('account:login')
        else:
            messages.error(request, 'No user found with that email address.')
            return redirect('account:forgot_password')
    return render(request, 'account/forgot-password.html')

def new_password(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect('core:index')

    uid = force_str(urlsafe_base64_decode(uidb64))
    try:
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password1')
            confirm_new_password = request.POST.get('new_password2')
            if new_password == confirm_new_password:
                user.set_password(new_password)
                user.save()

                messages.success(request, 'Your password has been successfully updated.')
                print("Your password has been successfully updated.")
                return redirect('account:login')
            else:
                messages.error(request, 'Passwords do not match.')
                print('Passwords do not match.')
                return redirect('account:new_password', uidb64=uidb64, token=token)
    else:
        messages.error(request, 'The password reset link is invalid.')

    return render(request, 'account/new_password.html', {'uidb64': uidb64, 'token': token})

import pycountry

@login_required
def Profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phoneNumber', user.phone_number)
        user.fb_id = request.POST.get('fb_id', user.fb_id)
        user.address = request.POST.get('address', user.address)
        user.country = request.POST.get('country', user.country)
        user.city = request.POST.get('city', user.city)
        user.post_code = request.POST.get('postCode', user.post_code)
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        user.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect('account:profile')
    countries = [country.name for country in pycountry.countries]
    return render(request, 'account/profile.html', {'countries': countries})