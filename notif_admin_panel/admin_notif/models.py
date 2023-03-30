import uuid

from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField


class NotifChoices(models.TextChoices):
    user_create = "user_create"
    change_password = "change_password"
    new_films = "new_films"
    received_likes = "received_likes"


class Notification(models.Model):
    """Для просмотра ивентов."""
    id = models.UUIDField('id',
                          primary_key=True,
                          default=uuid.uuid4,
                          unique=True,
                          null=False,
                          max_length=127)
    notification_type = models.CharField(choices=NotifChoices.choices,
                                         max_length=255)
    notification_text = models.CharField(null=True, max_length=255)
    notification_data = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False, null=False)
    ready = models.BooleanField(default=False, null=False)
    user_id = models.UUIDField(max_length=127)
    user_name = models.CharField (null=True, max_length=255)
    user_email = models.CharField (null=True, max_length=255)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "notifications"
        managed = False

class AdminNotifEvent(models.Model):
    """Только создает список id, ивенты для сендера создаст енрич воркер."""
    id = models.UUIDField('id',
                          primary_key=True,
                          default=uuid.uuid4,
                          unique=True,
                          null=False,
                          max_length=255)
    notification_type = models.CharField(choices=NotifChoices.choices,
                                         max_length=255,
                                         default=NotifChoices.new_films)
    notification_data = models.DateTimeField(auto_now=True)
    notification_text = models.CharField (null=True, max_length=511)
    status = models.BooleanField('status', default=False)
    user_ids = ArrayField(models.UUIDField(max_length=127))

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "adminnotifevent"
        managed = False
