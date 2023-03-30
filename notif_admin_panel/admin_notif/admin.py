from admin_notif.models import AdminNotifEvent, Notification
from django.contrib import admin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin


@admin.register(Notification)
class ResponseGetCreateUserAdmin(admin.ModelAdmin):
    empty_value_display = '-empty-'


@admin.register(AdminNotifEvent)
class ResponseGetReviewLikeAdmin(admin.ModelAdmin, DynamicArrayMixin):
    empty_value_display = '-empty-'

