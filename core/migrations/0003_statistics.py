# Generated by Django 5.1.3 on 2024-11-27 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_publisherplacement'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('impression', models.PositiveIntegerField()),
                ('clicks', models.PositiveIntegerField()),
                ('ctr', models.FloatField()),
                ('cpm', models.FloatField()),
                ('revenue', models.FloatField()),
            ],
            options={
                'unique_together': {('date',)},
            },
        ),
    ]
