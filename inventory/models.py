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

    def __str__(self):
        return f"{self.full_name} ({self.position})"

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


class Device(models.Model):
    """Модель оборудования/устройств"""

    # Статусы оборудования как константы
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
        DeviceType,  # Ссылка на модель DeviceType
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


class Request(models.Model):
    """Модель заявок на оборудование"""

    # Статусы заявки
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
        on_delete=models.CASCADE,  # Если удаляем сотрудника - удаляем заявки
        verbose_name='Сотрудник'
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,  # Защищаем от удаления оборудования с активными заявками
        verbose_name='Оборудование'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус заявки'
    )
    purpose = models.TextField(
        blank=True,
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
        auto_now=True,  # Автообновление при КАЖДОМ изменении
        verbose_name='Дата обновления'
    )

    def __str__(self):
        return f"Заявка #{self.id} - {self.employee} ({self.status})"

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'