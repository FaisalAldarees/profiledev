from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.auth import get_user_model

import uuid
import os


def avatar_image_file_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join("uploads/avatar/", filename)


class UserProfile(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="profile",)
    avatar = models.ImageField(default="media/uploads/avatar/download.jpeg", upload_to=avatar_image_file_path,)
    job_experiences = ArrayField(JSONField(default=None, blank=True), default=None, blank=True, null=True,)
    education = ArrayField(JSONField(default=None, blank=True), default=None, blank=True, null=True,)
    certifications = ArrayField(JSONField(default=None, blank=True), default=None, blank=True, null=True,)
    about = models.TextField(default=None, null=True)
    social_info = ArrayField(JSONField(default=None, blank=True), default=None, blank=True, null=True,)
    skills = ArrayField(models.CharField(max_length=32), default=None, blank=True, null=True)
