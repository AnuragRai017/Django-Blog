# Generated by Django 5.0.4 on 2024-06-10 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_profile_birth_date_profile_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
