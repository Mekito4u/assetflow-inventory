from django.contrib import messages
from django.shortcuts import render, get_object_or_404,redirect
from django.utils import timezone
from django.contrib.auth import authenticate, login
from .decorators import role_required
from .models import *


@role_required(['admin', 'tech', 'employee'])
def device_list(request):
    devices = Device.objects.all().select_related('device_type')

    user_has_device = {}
    if request.user.is_authenticated and hasattr(request.user, 'employee'):
        employee_devices = Request.objects.filter(
            employee=request.user.employee,
            status=Request.STATUS_APPROVED
        ).values_list('device_id', flat=True)
        user_has_device = {device_id: True for device_id in employee_devices}

    stats = {
        'total': devices.count(),
        'available': devices.filter(status='available').count(),
        'in_use': devices.filter(status='in_use').count(),
    }

    return render(request, 'inventory/device_list.html', {
        'devices': devices,
        'stats': stats,
        'user_has_device': user_has_device,
        'title': 'Весь инвентарь компании'
    })


@role_required(['admin', 'tech', 'employee'])
def employee_devices(request, employee_id):
    if not request.user.is_authenticated:
        return redirect('login')
    """Страница оборудования конкретного сотрудника"""
    employee = get_object_or_404(Employee, id=employee_id)
    employee_requests = Request.objects.filter(employee=employee).select_related('device')

    return render(request, 'inventory/employee_devices.html', {
        'employee': employee,
        'requests': employee_requests
    })


@role_required(['employee'])
def create_request(request, device_id):
    device = get_object_or_404(Device, id=device_id)

    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Профиль сотрудника не найден')
        return redirect('device_list')

    if request.method == 'POST':
        purpose = request.POST.get('purpose')

        if device.status != Device.STATUS_AVAILABLE:
            messages.error(request, 'Оборудование уже занято')
            return redirect('device_list')

        if Request.objects.filter(device=device, status=Request.STATUS_PENDING).exists():
            messages.error(request, 'На это оборудование уже есть активная заявка')
            return redirect('device_list')

        Request.objects.create(
            employee=employee,
            device=device,
            purpose=purpose,
            status=Request.STATUS_PENDING
        )

        messages.success(request, 'Заявка создана')
        return redirect('device_list')

    return render(request, 'inventory/create_request.html', {
        'device': device
    })


@role_required(['admin'])
def manage_requests(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.username != "admin":
        messages.error(request, 'Требуются права администратора')
        return redirect('device_list')


    pending_requests = Request.objects.filter(status=Request.STATUS_PENDING)
    active_requests = Request.objects.filter(status=Request.STATUS_APPROVED)

    repairs = {}
    for req in active_requests:
        active_repair = Repair.objects.filter(device=req.device, status=Repair.STATUS_REPAIRING).first()
        if active_repair:
            repairs[req.id] = active_repair

    return render(request, 'inventory/manage_requests.html', {
        'pending_requests': pending_requests,
        'active_requests': active_requests,
        'repairs': repairs
    })


@role_required(['admin'])
def update_request_status(request, request_id, new_status):
    if not request.user.is_authenticated or request.user.userprofile.role != 'admin':
        messages.error(request, 'Требуются права администратора')
        return redirect('device_list')

    req = get_object_or_404(Request, id=request_id)

    if new_status in [Request.STATUS_APPROVED, Request.STATUS_REJECTED]:
        req.status = new_status
        req.save()

        # Записываем в историю при одобрении
        if new_status == Request.STATUS_APPROVED:
            EquipmentMovement.objects.create(
                device=req.device,
                employee=req.employee,
                movement_type=EquipmentMovement.MOVEMENT_ISSUE,
                notes=f'Выдача по заявке #{req.id}'
            )

        messages.success(request, f'Заявка {new_status}')

    return redirect('manage_requests')


@role_required(['admin'])
def return_device(request, request_id):
    req = get_object_or_404(Request, id=request_id)

    if req.status != Request.STATUS_APPROVED:
        messages.error(request, 'Можно возвращать только одобренные заявки')
        return redirect('manage_requests')

    req.status = Request.STATUS_COMPLETED
    req.save()

    EquipmentMovement.objects.create(
        device=req.device,
        employee=req.employee,
        movement_type=EquipmentMovement.MOVEMENT_RETURN,
        notes=f'Возврат по заявке #{req.id}'
    )

    messages.success(request, f'Оборудование {req.device.model} возвращено')
    return redirect('manage_requests')


@role_required(['employee'])
def report_breakdown(request, device_id):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Профиль сотрудника не найден')
        return redirect('device_list')

    device = get_object_or_404(Device, id=device_id)

    active_request = Request.objects.filter(
        device=device,
        employee=employee,
        status=Request.STATUS_APPROVED
    ).first()

    if not active_request:
        messages.error(request, 'Вы можете сообщать о поломке только своего оборудования')
        return redirect('device_list')

    if device.status != Device.STATUS_IN_USE:
        messages.error(request, 'Оборудование должно быть в использовании')
        return redirect('device_list')

    if request.method == 'POST':
        description = request.POST.get('description')

        repair = Repair.objects.create(
            device=device,
            reported_by=employee,
            description=description,
            status=Repair.STATUS_REPAIRING
        )

        device.status = Device.STATUS_BROKEN
        device.save()

        EquipmentMovement.objects.create(
            device=device,
            employee=employee,
            movement_type=EquipmentMovement.MOVEMENT_REPAIR,
            notes=f'Поломка: {description}'
        )

        messages.success(request, 'Поломка зарегистрирована')
        return redirect('device_list')

    return render(request, 'inventory/report_breakdown.html', {
        'device': device
    })


@role_required(['employee'])
def request_extension(request, request_id):
    if not request.user.is_authenticated:
        return redirect('login')
    req = get_object_or_404(Request, id=request_id)

    if request.method == 'POST':
        new_date = request.POST.get('new_return_date')
        reason = request.POST.get('reason')

        Extension.objects.create(
            original_request=req,
            new_return_date=new_date,
            reason=reason,
            status=Request.STATUS_PENDING
        )

        messages.success(request, 'Заявка на продление создана')
        return redirect('employee_devices', employee_id=req.employee.id)

    return render(request, 'inventory/request_extension.html', {
        'request': req
    })


@role_required(['tech'])
def repair_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    repairs = Repair.objects.filter(status=Repair.STATUS_REPAIRING)
    return render(request, 'inventory/repair_list.html', {
        'repairs': repairs
    })


@role_required(['tech'])
def complete_repair(request, repair_id):
    if not request.user.is_authenticated:
        return redirect('login')
    repair = get_object_or_404(Repair, id=repair_id)

    if request.method == 'POST':
        repair.status = Repair.STATUS_COMPLETED
        repair.completed_at = timezone.now()
        repair.assigned_tech = request.user
        repair.save()

        repair.device.status = Device.STATUS_AVAILABLE
        repair.device.save()

        messages.success(request, 'Ремонт завершен')
        return redirect('repair_list')

    return render(request, 'inventory/complete_repair.html', {
        'repair': repair
    })


@role_required(['analyst'])
def equipment_report(request):
    if not request.user.is_authenticated:
        return redirect('login')
    movements = EquipmentMovement.objects.all().select_related('device', 'employee')[:10]
    return render(request, 'inventory/equipment_report.html', {
        'movements': movements
    })


@role_required(['analyst'])
def breakdown_statistics(request):
    if not request.user.is_authenticated:
        return redirect('login')
    repairs = Repair.objects.all()
    total_repairs = repairs.count()
    completed_repairs = repairs.filter(status=Repair.STATUS_COMPLETED).count()

    return render(request, 'inventory/breakdown_statistics.html', {
        'total_repairs': total_repairs,
        'completed_repairs': completed_repairs,
        'repairs': repairs
    })


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            try:
                profile = UserProfile.objects.get(user=user)
                if profile.role == UserProfile.ROLE_ADMIN:
                    return redirect('manage_requests')
                elif profile.role == UserProfile.ROLE_TECH:
                    return redirect('repair_list')
                elif profile.role == UserProfile.ROLE_ANALYST:
                    return redirect('equipment_report')
                else:
                    return redirect('device_list')
            except UserProfile.DoesNotExist:
                return redirect('device_list')
        else:
            messages.error(request, 'Неверный логин или пароль')

    return render(request, 'inventory/login.html')