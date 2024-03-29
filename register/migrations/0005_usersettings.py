# Generated by Django 3.2.13 on 2022-10-11 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('register', '0004_longlivedtoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='settings', serialize=False, to='auth.user')),
                ('ricked', models.BooleanField(default=False)),
            ],
        ),
    ]
