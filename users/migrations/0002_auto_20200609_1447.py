# Generated by Django 3.0.7 on 2020-06-09 14:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='social_links',
            new_name='social_info',
        ),
    ]
