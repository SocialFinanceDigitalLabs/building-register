# Generated by Django 3.2.13 on 2023-04-27 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0005_usersettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactdetails',
            name='method',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='contactdetails',
            name='value',
            field=models.CharField(max_length=255),
        ),
    ]
