# Generated by Django 4.2.7 on 2023-12-13 19:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_postmodel_unique_user'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='postmodel',
            name='Unique user',
        ),
    ]
