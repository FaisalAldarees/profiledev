# Generated by Django 3.0.7 on 2020-08-13 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_userprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='headline',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
