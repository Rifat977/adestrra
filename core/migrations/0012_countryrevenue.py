# Generated by Django 5.1.3 on 2024-12-02 11:00

import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_adstatistics_clicks_remove_adstatistics_cpm_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryRevenue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('impressions', models.PositiveIntegerField(default=0)),
                ('revenue', models.FloatField(default=0.0)),
            ],
            options={
                'unique_together': {('country',)},
            },
        ),
    ]
