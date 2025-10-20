from django.core.exceptions import ValidationError
from django.db import models


class DeviceType(models.Model):
    """Модель для типов оборудования (Ноутбук, Монитор, Мышь)"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название типа'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип оборудования"
        verbose_name_plural = "Типы оборудования"


class Employee(models.Model):
    """Модель сотрудников компании"""
    full_name = models.CharField(
        max_length=100,
        verbose_name='ФИО'
    )
    position = models.CharField(
        max_length=100,
        verbose_name='Должность'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Отдел'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} ({self.position})"

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


class Device(models.Model):
    """Модель оборудования/устройств"""

    STATUS_AVAILABLE = 'available'
    STATUS_IN_USE = 'in_use'
    STATUS_BROKEN = 'broken'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Доступно'),
        (STATUS_IN_USE, 'В использовании'),
        (STATUS_BROKEN, 'На ремонте'),
    ]

    inventory_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Инвентарный номер'
    )
    model = models.CharField(
        max_length=100,
        verbose_name='Модель'
    )
    device_type = models.ForeignKey(
        DeviceType,
        on_delete=models.PROTECT,
        verbose_name='Тип оборудования'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
        verbose_name='Статус'
    )
    purchase_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата покупки'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f"{self.model} ({self.inventory_number})"

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'

    responsible_person = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                           verbose_name='МОЛ')
    is_written_off = models.BooleanField(default=False, verbose_name='Списано')
    write_off_reason = models.TextField(blank=True, verbose_name='Причина списания')
    write_off_date = models.DateField(null=True, blank=True, verbose_name='Дата списания')


class Request(models.Model):
    """Модель заявок на оборудование"""

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'На рассмотрении'),
        (STATUS_APPROVED, 'Одобрена'),
        (STATUS_REJECTED, 'Отклонена'),
        (STATUS_COMPLETED, 'Завершена'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name='Сотрудник'
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        verbose_name='Оборудование'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус заявки'
    )
    purpose = models.TextField(
        blank=False,
        verbose_name='Цель использования'
    )
    planned_return_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Планируемая дата возврата'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    ai_priority_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name='AI Оценка приоритета',
        help_text='1 (низкий) - 10 (критичный)'
    )
    ai_tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name='AI Теги',
        help_text='Автоматические теги от AI'
    )
    ai_summary = models.TextField(
        blank=True,
        verbose_name='AI Резюме',
        help_text='Краткое описание проблемы от AI'
    )
    ai_needs_clarification = models.BooleanField(
        default=False,
        verbose_name='AI: Требует уточнений',
        help_text='Заявка требует дополнительных уточнений по мнению AI'
    )

    def save(self, *args, **kwargs):
        """
        Сохраняет заявку с автоматической бизнес-логикой:
        - Обновляет статусы оборудования
        - Запускает AI-анализ для новых заявок
        """
        is_new = self.pk is None

        if not is_new:
            old_request = Request.objects.get(pk=self.pk)
            old_status = old_request.status
        else:
            old_status = None

        super().save(*args, **kwargs)

        # Бизнес-логика статусов оборудования
        if self.status == self.STATUS_APPROVED:
            self.device.status = Device.STATUS_IN_USE
            self.device.save()
        elif self.status == self.STATUS_COMPLETED:
            active_repair = Repair.objects.filter(device=self.device, status=Repair.STATUS_REPAIRING).exists()
            if active_repair:
                self.device.status = Device.STATUS_BROKEN
            else:
                self.device.status = Device.STATUS_AVAILABLE
            self.device.save()
        elif old_status == self.STATUS_APPROVED and self.status != self.STATUS_APPROVED:
            active_repair = Repair.objects.filter(device=self.device, status=Repair.STATUS_REPAIRING).exists()
            if active_repair:
                self.device.status = Device.STATUS_BROKEN
            else:
                self.device.status = Device.STATUS_AVAILABLE
            self.device.save()

        # AI-анализ для новых заявок
        if is_new and self.purpose:
            try:
                self.analyze_with_ai()
            except Exception:
                # Не ломаем сохранение заявки из-за ошибки AI
                pass

    def delete(self, *args, **kwargs):
        if self.status == self.STATUS_APPROVED:
            self.device.status = Device.STATUS_AVAILABLE
            self.device.save()
        super().delete(*args, **kwargs)

    def clean(self):
        if self.device.status != Device.STATUS_AVAILABLE and self.status == self.STATUS_PENDING:
            raise ValidationError('Оборудование уже занято')

        if Request.objects.filter(device=self.device, status=self.STATUS_PENDING).exclude(id=self.id).exists():
            raise ValidationError('На это оборудование уже есть активная заявка')

    def analyze_with_ai(self):
        """
        Запускает AI-анализ заявки и сохраняет результаты

        Автоматически определяет приоритет, теги и резюме на основе
        данных сотрудника, оборудования и цели использования
        """
        try:
            from .services.gigachat_service import GigaChatService

            service = GigaChatService()

            employee_position = getattr(self.employee, 'position', 'Не указана')
            device_type = self.device.device_type.name

            result = service.analyze_request(
                employee_position=employee_position,
                device_type=device_type,
                purpose=self.purpose
            )

            self.ai_priority_score = result.get('priority_score', 5)
            self.ai_tags = result.get('tags', [])
            self.ai_summary = result.get('summary', '')
            self.ai_needs_clarification = result.get('needs_clarification', False)

            self.save(update_fields=[
                'ai_priority_score', 'ai_tags', 'ai_summary',
                'ai_needs_clarification'
            ])

        except Exception:
            # Не прерываем работу системы из-за ошибок AI
            pass

    def get_priority_badge(self):
        """
        Возвращает HTML для цветного бейджа приоритета

        Returns:
            str: HTML span с цветным бейджем приоритета
        """
        from django.utils.safestring import mark_safe

        if not self.ai_priority_score:
            return mark_safe(
                '<span style="display: inline-block; padding: 4px 8px; background: #6c757d; color: white; border-radius: 4px; font-weight: bold;">—</span>')

        score = self.ai_priority_score

        if score >= 8:
            color = '#dc3545'  # красный
        elif score >= 5:
            color = '#ffc107'  # желтый
        else:
            color = '#28a745'  # зеленый

        return mark_safe(
            f'<span style="display: inline-block; padding: 4px 8px; background: {color}; color: white; border-radius: 4px; font-weight: bold;">{score}</span>')

    get_priority_badge.allow_tags = True
    get_priority_badge.short_description = 'Приоритет'

    def __str__(self):
        return f"Заявка #{self.id} - {self.employee} ({self.status})"

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class UserProfile(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_TECH = 'tech'
    ROLE_EMPLOYEE = 'employee'
    ROLE_ANALYST = 'analyst'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Администратор учёта'),
        (ROLE_TECH, 'Технический специалист'),
        (ROLE_EMPLOYEE, 'Сотрудник'),
        (ROLE_ANALYST, 'Аналитик'),
    ]

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_EMPLOYEE)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Repair(models.Model):
    STATUS_REPAIRING = 'repairing'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_REPAIRING, 'В ремонте'),
        (STATUS_COMPLETED, 'Отремонтировано'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reported_repairs')
    assigned_tech = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REPAIRING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class Extension(models.Model):
    original_request = models.ForeignKey(Request, on_delete=models.CASCADE)
    new_return_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Request.STATUS_CHOICES, default=Request.STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)


class EquipmentMovement(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=50, choices=[
        ('issue', 'Выдача'),
        ('return', 'Возврат'),
        ('repair', 'Передача в ремонт'),
        ('write_off', 'Списание')
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)


class EquipmentMovement(models.Model):
    MOVEMENT_ISSUE = 'issue'
    MOVEMENT_RETURN = 'return'
    MOVEMENT_REPAIR = 'repair'
    MOVEMENT_WRITE_OFF = 'write_off'
    MOVEMENT_CHOICES = [
        (MOVEMENT_ISSUE, 'Выдача'),
        (MOVEMENT_RETURN, 'Возврат'),
        (MOVEMENT_REPAIR, 'Передача в ремонт'),
        (MOVEMENT_WRITE_OFF, 'Списание'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.device} - {self.get_movement_type_display()} - {self.timestamp}"

    class Meta:
        verbose_name = 'Движение оборудования'
        verbose_name_plural = 'Движения оборудования'
        ordering = ['-timestamp']
