# Generated by Django 3.0.7 on 2020-06-23 22:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20200623_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremailverification',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
