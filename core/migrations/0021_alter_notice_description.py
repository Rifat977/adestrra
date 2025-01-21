# Generated by Django 5.1.3 on 2024-12-19 21:33

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_alter_adstatistics_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notice',
            name='description',
            field=ckeditor.fields.RichTextField(help_text='Detailed notice text', verbose_name='Description'),
        ),
    ]
