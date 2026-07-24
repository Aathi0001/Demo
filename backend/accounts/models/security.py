''' Fields

security_id
user

lock_password
delete_password

anime_delete_after_hours
worklog_delete_after_hours
notes_delete_after_hours
expense_delete_after_hours

lock_password_reset_at
delete_password_reset_at
'''
from django.contrib.auth.models import User
from django.db import models

from common.models import BaseModel


class Security(BaseModel):
    """
    Stores lock password, delete password and auto-delete settings.
    """

    user = models.OneToOneField( User, on_delete=models.CASCADE, related_name="security")

    lock_password = models.CharField( max_length=255, blank=True, null=True )

    delete_password = models.CharField( max_length=255, blank=True, null=True )

    anime_delete_after_hours = models.PositiveIntegerField( default=48 )

    worklog_delete_after_hours = models.PositiveIntegerField( default=48 )

    notes_delete_after_hours = models.PositiveIntegerField( default=48 )

    expense_delete_after_hours = models.PositiveIntegerField( default=48 )

    lock_password_reset_at = models.DateTimeField( blank=True, null=True )

    delete_password_reset_at = models.DateTimeField( blank=True, null=True )

    class Meta:
        db_table = "security"

    def __str__(self):
        return self.user.username
