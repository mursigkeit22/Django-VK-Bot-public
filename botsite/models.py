from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """ CharFields and TextFields are never saved as NULL in Django . Blank values are stored in the DB as an empty string ('').
     So null=True is unnecessary.
     However, you can manually set one of these fields to None to force set it as NULL.
     If you have a scenario where that might be necessary, you should still include null=True."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    vk_id = models.BigIntegerField(unique=True)
    vk_token = models.CharField(max_length=200, blank=True)
