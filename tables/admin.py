from django.contrib import admin
from .models import Table, QRSession

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'is_active')

@admin.register(QRSession)
class QRSessionAdmin(admin.ModelAdmin):
    list_display = ('table', 'token', 'created_at', 'is_active')