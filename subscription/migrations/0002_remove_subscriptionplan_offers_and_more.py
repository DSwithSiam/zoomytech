# Generated by Django 5.1.5 on 2025-05-13 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriptionplan',
            name='offers',
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='features',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='popular',
            field=models.BooleanField(default=False),
        ),
    ]
