from django.shortcuts import render, get_object_or_404
from .models import Device, Employee, Request


def device_list(request):
    """Главная страница - список всего оборудования"""
    devices = Device.objects.all().select_related('device_type')

    # Статистика для отображения
    stats = {
        'total': devices.count(),
        'available': devices.filter(status='available').count(),
        'in_use': devices.filter(status='in_use').count(),
    }

    return render(request, 'inventory/device_list.html', {
        'devices': devices,
        'stats': stats,
        'title': '📊 Весь инвентарь компании'
    })


def employee_devices(request, employee_id):
    """Страница оборудования конкретного сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)
    employee_requests = Request.objects.filter(employee=employee).select_related('device')

    return render(request, 'inventory/employee_devices.html', {
        'employee': employee,
        'requests': employee_requests
    })