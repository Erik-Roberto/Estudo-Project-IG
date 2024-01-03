# Generated by Django 4.2.7 on 2023-12-13 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_postmodel_likes_postmodel_user'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='postmodel',
            constraint=models.UniqueConstraint(fields=('user',), name='Unique user'),
        ),
    ]
