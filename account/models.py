from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from decimal import Decimal


class CustomUser(AbstractUser):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Reject', 'Reject'),
    ]
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Inactive')
    balance = models.FloatField(default=0.0)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone_number = models.CharField(max_length=20, blank=True, default='')
    fb_id = models.CharField(max_length=100, blank=True, default='')
    address = models.CharField(max_length=200, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    post_code = models.CharField(max_length=20, blank=True, default='')
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "User Management"

    # def is_email_verification_token_expired(self):
    #     if self.email_verification_sent_at:
    #         expiration_time = timezone.timedelta(hours=24)  # 24 hours validity
    #         return self.email_verification_sent_at + expiration_time < timezone.now()
    #     return True

    # def generate_password_reset_token(self):
    #     token = get_random_string(length=32)
    #     self.password_reset_token = token
    #     self.save()
    #     return token

# @receiver(models.signals.pre_save, sender=CustomUser)
# def notify_user_on_approval(sender, instance, **kwargs):
#     if instance.pk:
#         try:
#             old_instance = CustomUser.objects.get(pk=instance.pk)
#         except CustomUser.DoesNotExist:
#             return

#         if instance.is_approved and not old_instance.is_approved and instance.is_verified:
#             send_mail(
#                 'Your profile has been approved',
#                 'Your profile has been approved. You can now access the site.',
#                 'Entrance Quiz <support@entrancequiz.com>',
#                 [instance.email],
#                 fail_silently=False,
#             )


from django.utils import timezone
from django.db import transaction



class UserBalanceWithdrawal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DECLINED', 'Declined'),
    ]

    PAYMENT_METHOD = [
        ('Paypal', 'Paypal'),
        ('Payoneer', 'Payoneer'),
        ('Binance', 'Binance'),
        ('Bank', 'Bank'),
        ('Others', 'Others'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD, default='Paypal')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    admin_note = models.TextField(null=True, blank=True)

    account_number = models.CharField(max_length=50, null=True, blank=True)  
    account_details = models.TextField(null=True, blank=True)  

    class Meta:
        ordering = ['-requested_at']
        verbose_name = "User Balance Withdrawal"
        verbose_name_plural = "Withdraw Request"

    def __str__(self):
        return f"User: {self.user.username} | Amount: ${self.amount} | Status: {self.status}"

    def approve(self, note=None):
        if self.status != 'PENDING':
            raise ValueError("Only pending withdrawals can be approved.")
        if self.user.balance < self.amount:
            raise ValueError("Insufficient balance.")
        
        with transaction.atomic():
            self.user.balance = Decimal(self.user.balance) 
            self.status = 'APPROVED'
            self.processed_at = timezone.now()

            self.user.balance -= self.amount
            self.user.save(update_fields=['balance']) 
            self.admin_note = note

            self.save(update_fields=['status', 'processed_at', 'admin_note']) 

    def decline(self, note=None):
        if self.status != 'PENDING':
            raise ValueError("Only pending withdrawals can be declined.")

        with transaction.atomic():
            self.status = 'DECLINED'
            self.processed_at = timezone.now()
            self.admin_note = note

            self.save(update_fields=['status', 'processed_at', 'admin_note'])  


from urllib.parse import urlparse, urlunparse


def format_url(url):
    parsed_url = urlparse(url)
    formatted_path = parsed_url.path.rstrip('/')
    formatted_url = urlunparse(
        parsed_url._replace(path=formatted_path)
    )
    return formatted_url


class Settings(models.Model):
    domain = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)
    commission = models.IntegerField(default=0)
    email = models.EmailField(unique=True, null=True, blank=True)
    skype = models.CharField(max_length=255, null=True, blank=True)
    contact_page_email = models.EmailField(unique=True, null=True, blank=True)
    contact_page_skype = models.CharField(max_length=255, null=True, blank=True)
    notice = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.domain:
            self.domain = format_url(self.domain)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.domain

    class Meta:
        verbose_name_plural = "Site Settings"

class AdminRevenueStatistics(models.Model):
    date = models.DateField(auto_now_add=True) 
    total_revenue = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.00'))
    publisher_revenue = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.00'))
    admin_revenue = models.DecimalField(max_digits=15, decimal_places=4, default=Decimal('0.00'))
    total_impressions = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = "Admin Revenue Statistics"
        verbose_name_plural = "Admin Revenue Statistics"
        ordering = ['-date']

    def __str__(self):
        return f"Statistics for {self.date}"

    # @property
    # def admin_commission_percentage(self):
    #     if self.total_revenue > 0:
    #         return (self.admin_revenue / self.total_revenue) * 100
    #     return 0
