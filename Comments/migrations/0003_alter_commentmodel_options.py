# Generated by Django 4.2.7 on 2024-01-11 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_commentmodel_post_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commentmodel',
            options={'ordering': ['-fixed', 'post_date']},
        ),
    ]