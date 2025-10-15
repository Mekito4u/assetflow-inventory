from django.contrib import admin

from .models import *


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'department', 'email')
    list_filter = ('department', 'position')
    search_fields = ('full_name', 'email')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('inventory_number', 'model', 'device_type', 'status')
    list_filter = ('device_type', 'status')
    search_fields = ('inventory_number', 'model')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'device', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ['device', 'reported_by', 'status', 'created_at']


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    list_display = ['original_request', 'new_return_date', 'status']


@admin.register(EquipmentMovement)
class EquipmentMovementAdmin(admin.ModelAdmin):
    list_display = ['device', 'employee', 'movement_type', 'timestamp']
