# Generated by Django 4.1 on 2023-10-03 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailbox',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активность'),
        ),
    ]
