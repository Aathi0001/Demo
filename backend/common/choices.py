from django.db import models


class DeleteStatus(models.IntegerChoices):
    ACTIVE = 0, "Active"
    SCHEDULED = 1, "Scheduled for Deletion"
    DELETED = 2, "Deleted"
