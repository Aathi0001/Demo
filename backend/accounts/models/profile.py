''' Fields 

profile_id
user
display_name
theme
timezone
created_at
updated_at
'''
from django.contrib.auth.models import User
from django.db import models

from common.models import BaseModel


class Profile(BaseModel):
    """
    Stores additional information about a user.
    """

    THEME_CHOICES = [ ("light", "Light"), ("dark", "Dark"), ("system", "System"), ]

    user = models.OneToOneField( User, on_delete=models.CASCADE, related_name="profile")

    display_name = models.CharField( max_length=100 )

    theme = models.CharField( max_length=10, choices=THEME_CHOICES, default="system" )

    timezone = models.CharField( max_length=100, default="Asia/Kolkata" )

    class Meta:
        db_table = "profile"

    def __str__(self):
        return self.display_name
