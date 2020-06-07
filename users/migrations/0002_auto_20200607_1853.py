# Generated by Django 3.0.7 on 2020-06-07 18:53

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='avatar',
            field=models.ImageField(default='media/uploads/avatar/download.jpeg', upload_to=users.models.avatar_image_file_path),
        ),
    ]
