# Generated by Django 3.0.7 on 2020-06-16 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20200616_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useremailverification',
            name='resent_at',
            field=models.DateTimeField(null=True),
        ),
    ]
