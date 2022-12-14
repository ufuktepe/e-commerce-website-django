# Generated by Django 3.1.6 on 2021-03-08 03:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_auto_20210307_1122'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='listing',
            options={'ordering': ['-created_on']},
        ),
        migrations.AddField(
            model_name='listing',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
