# Generated by Django 5.1.3 on 2024-12-02 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jabaa_admin_dashboard', '0004_citizen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='citizen',
            name='age',
        ),
    ]
