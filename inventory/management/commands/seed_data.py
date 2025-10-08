import os
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import DeviceType, Employee, Device, Request


class Command(BaseCommand):
    help = 'Создает тестовые данные для демонстрации AssetFlow'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Запуск инициализации тестового предприятия...')

        # 1. Создаем группы и права
        self.create_groups()

        # 2. Создаем тестовые данные
        self.create_sample_data()

        self.stdout.write(
            self.style.SUCCESS('✅ Тестовое предприятие успешно создано!')
        )

    def create_groups(self):
        """Создает группы пользователей с разными правами"""

        # Группа администраторов учета
        admin_group, created = Group.objects.get_or_create(
            name='Администраторы учета'
        )

        # Группа технических специалистов
        tech_group, created = Group.objects.get_or_create(
            name='Технические специалисты'
        )

        self.stdout.write('✅ Группы пользователей созданы')

    def create_sample_data(self):
        """Создает тестовые данные предприятия"""

        # Типы оборудования
        laptop_type, _ = DeviceType.objects.get_or_create(
            name='Ноутбук',
            defaults={'description': 'Мобильные компьютеры для работы'}
        )
        monitor_type, _ = DeviceType.objects.get_or_create(
            name='Монитор',
            defaults={'description': 'Дисплеи для рабочих станций'}
        )

        # Сотрудники
        ivanov, _ = Employee.objects.get_or_create(
            full_name='Иванов Иван Иванович',
            defaults={
                'position': 'Разработчик',
                'department': 'IT',
                'email': 'i.ivanov@company.ru'
            }
        )

        petrova, _ = Employee.objects.get_or_create(
            full_name='Петрова Анна Сергеевна',
            defaults={
                'position': 'Тестировщик',
                'department': 'QA',
                'email': 'a.petrova@company.ru'
            }
        )

        # Оборудование
        laptop1, _ = Device.objects.get_or_create(
            inventory_number='NB001',
            defaults={
                'model': 'Dell Latitude 5520',
                'device_type': laptop_type,
                'status': 'available'
            }
        )

        monitor1, _ = Device.objects.get_or_create(
            inventory_number='MON001',
            defaults={
                'model': 'Samsung S24R350',
                'device_type': monitor_type,
                'status': 'available'
            }
        )

        # Заявки
        request1, _ = Request.objects.get_or_create(
            employee=ivanov,
            device=laptop1,
            defaults={
                'status': 'approved',
                'purpose': 'Для разработки нового функционала'
            }
        )

        self.stdout.write('✅ Тестовые данные созданы')
        self.stdout.write('')
        self.stdout.write('📊 Создано:')
        self.stdout.write(f'   - Типов оборудования: {DeviceType.objects.count()}')
        self.stdout.write(f'   - Сотрудников: {Employee.objects.count()}')
        self.stdout.write(f'   - Устройств: {Device.objects.count()}')
        self.stdout.write(f'   - Заявок: {Request.objects.count()}')