from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.urls import reverse

from django_countries.fields import CountryField
from decimal import Decimal

from django.contrib.auth import get_user_model
from account.models import Settings

User = get_user_model()


# Create your models here.
class PublisherPlacement(models.Model):
    id = models.BigIntegerField(primary_key=True)
    domain_id = models.BigIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  
    image = models.ImageField(upload_to="placements/images/", blank=True, null=True) 
    alias = models.CharField(max_length=255, blank=True, null=True)
    direct_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Publisher Smart Link"

class PlacementLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    placement = models.ForeignKey(PublisherPlacement, on_delete=models.CASCADE)
    link = models.URLField(max_length=1024, null=True, blank=True)  
    subid = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'placement')
        verbose_name_plural = "User Smart Link"

    def save(self, *args, **kwargs):
        if not self.link: 
            settings = Settings.objects.first()
            unique_id = uuid.uuid4()  
            relative_url = reverse('core:redirect_to_ad', kwargs={'placement_id': self.placement.id, 'unique_id': unique_id})
            domain = settings.domain
            self.link = f"{domain}{relative_url}"
        super().save(*args, **kwargs)

class AdStatistics(models.Model):
    placement = models.ForeignKey(PublisherPlacement, on_delete=models.CASCADE, related_name="ad_statistics")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ad_statistics")
    date = models.DateField(default=timezone.now)
    impressions = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=4, default=float('0.00'))


    class Meta:
        unique_together = ('placement', 'user', 'date')
        verbose_name_plural = "User Statistics"

    def __str__(self):
        return f"{self.user.username} - {self.placement.title} - {self.date}"


    
class VisitorLog(models.Model):
    placement_link = models.ForeignKey(PlacementLink, on_delete=models.CASCADE, related_name="visitor_logs")
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('placement_link', 'ip_address', 'visited_at')

    def __str__(self):
        return f"IP: {self.ip_address} | {self.visited_at}"


from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

class Notice(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"), help_text=_("Detailed notice text"))
    image = models.ImageField(
        upload_to='notices/',
        blank=True,
        null=True,
        verbose_name=_("Image"),
        help_text=_("Optional image for the notice")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Notice")
        verbose_name_plural = _("Notices")
        ordering = ['-created_at']

    def __str__(self):
        return self.title
