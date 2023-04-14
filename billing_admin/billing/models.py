import uuid

from django.db import models


class UserStatus(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expires_at = models.DateTimeField(auto_now_add=False)
    actual = models.BooleanField()
    expires_status = models.BooleanField()

    class Meta:
        db_table = "public\".\"userstatus"


class Tariff(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    days = models.DurationField()
    price = models.FloatField(blank=False)
    description = models.CharField('description', max_length=127)

    class Meta:
        db_table = "public\".\"tariff"


class PaymentPG(models.Model):
    class StatusEnum(models.TextChoices):
        succeeded = "succeeded"
        canceled = "canceled"
        pending = "pending"
        refund = "refund"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=False)
    payment = models.CharField('payment', max_length=127)
    income = models.FloatField(blank=False)
    status = models.CharField(max_length=9, choices=StatusEnum.choices)
    tariff = models.ForeignKey("Tariff", on_delete=models.CASCADE)
    userstatus = models.ForeignKey('UserStatus', on_delete=models.CASCADE)

    class Meta:
        db_table = "public\".\"payment"
