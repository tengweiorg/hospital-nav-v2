# Generated by Django 5.1.7 on 2025-03-08 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navigator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='click_count',
            field=models.IntegerField(default=0),
        ),
    ]
