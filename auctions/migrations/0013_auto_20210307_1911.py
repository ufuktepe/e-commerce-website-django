# Generated by Django 3.1.6 on 2021-03-08 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_auto_20210307_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]
