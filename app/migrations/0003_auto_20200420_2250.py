# Generated by Django 2.2.11 on 2020-04-20 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20200420_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='poem',
            name='locked_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='poem',
            name='locked_by_anonymous',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='poem',
            name='locked_by_user',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='poem',
            name='unraveled',
            field=models.BooleanField(default=False),
        ),
    ]