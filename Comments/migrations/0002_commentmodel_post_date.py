# Generated by Django 4.2.7 on 2024-01-09 17:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentmodel',
            name='post_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]