from django.db import models

from django.contrib.auth.models import User

# Create your models here.

User.add_to_class('device_img', models.TextField(blank=True, null=True, default=''))
User.add_to_class('provisioning_uri', models.TextField(blank=True, null=True, default=''))
