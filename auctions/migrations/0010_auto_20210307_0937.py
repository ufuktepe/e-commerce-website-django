# Generated by Django 3.1.6 on 2021-03-07 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_listing_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['date_posted']},
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
