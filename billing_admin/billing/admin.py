from django.contrib import admin
from .models import UserStatus, PaymentPG, Tariff

# Register your models here.
@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    pass

@admin.register(Tariff)
class UserStatusAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentPG)
class UserStatusAdmin(admin.ModelAdmin):
    pass