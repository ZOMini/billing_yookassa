from django.db import models
import uuid




class UserStatus(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,  editable=False)
    expires_at = models.DateTimeField(auto_now_add=False)
    actual = models.BooleanField
    expires_status = models.BooleanField
    payments = models.ForeignKey('PaymentPG', on_delete=models.CASCADE)
    class Meta:
        db_table = "public\".\"userstatus"



class Tariff(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    days = models.TextField(editable=False)
    price = models.FloatField(blank=False)
    description = models.CharField('description', max_length=127, editable=False)

    class Meta:
        db_table = "public\".\"tariff"


class PaymentPG(models.Model):
    class StatusEnum(models.TextChoices):
        succeeded = "succeeded"
        canceled = "canceled"
        pending = "pending"
        refund = "refund"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=False, editable=False)
    payment = models.CharField('payment', max_length=127, editable=False)
    income = models.FloatField(blank=False, editable=False)
    status = models.CharField(max_length=9, choices=StatusEnum.choices, editable=False)
    tariff_id = models.ForeignKey("Tariff", on_delete=models.CASCADE)
    userstatus_id = models.ForeignKey('UserStatus', on_delete=models.CASCADE)

    class Meta:
        db_table = "public\".\"payment"