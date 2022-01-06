from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=30, blank=False)
    key_pub = models.CharField(max_length=24, blank=False)
    key_secret = models.CharField(max_length=48, blank=False)
    hide_balance = models.BooleanField(default=False)
