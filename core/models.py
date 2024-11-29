from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.urls import reverse
from django.conf import settings


from django.contrib.auth import get_user_model

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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class AdStatistics(models.Model):
    placement = models.ForeignKey(PublisherPlacement, on_delete=models.CASCADE, related_name="ad_statistics")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ad_statistics")
    date = models.DateField(default=timezone.now)
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    ctr = models.FloatField(default=0.0)  
    cpm = models.FloatField(default=0.0) 
    revenue = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('placement', 'user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.placement.title} - {self.date}"


class PlacementLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    placement = models.ForeignKey(PublisherPlacement, on_delete=models.CASCADE)
    link = models.URLField(max_length=1024, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'placement')

    def save(self, *args, **kwargs):
        if not self.link: 
            unique_id = uuid.uuid4()  
            relative_url = reverse('core:redirect_to_ad', kwargs={'placement_id': self.placement.id, 'unique_id': unique_id})
            domain = settings.SITE_URL
            self.link = f"{domain}{relative_url}"
        super().save(*args, **kwargs)

    