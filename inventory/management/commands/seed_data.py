from django.core.management.base import BaseCommand
from inventory.models import DeviceType, Employee, Device, Request, UserProfile, Repair
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Создает тестовые данные для демонстрации AssetFlow'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')

        self.reset_data()

        self.create_device_types()
        self.create_employees()
        self.create_devices()
        self.create_requests()
        self.create_repairs()
        self.create_users_with_roles()

        self.stdout.write(self.style.SUCCESS('Тестовые данные созданы'))

    def reset_data(self):
        """Очистка данных в правильном порядке"""
        Repair.objects.all().delete()
        Request.objects.all().delete()
        Device.objects.all().delete()
        Employee.objects.all().delete()
        DeviceType.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def create_device_types(self):
        """Создаём типы оборудования"""
        types = [
            {'name': 'Ноутбук', 'description': 'Мобильные компьютеры'},
            {'name': 'Монитор', 'description': 'Дисплеи для рабочих станций'},
            {'name': 'Мышь', 'description': 'Компьютерные мыши'},
            {'name': 'Клавиатура', 'description': 'Проводные и беспроводные клавиатуры'},
            {'name': 'Док-станция', 'description': 'Станции для подключения ноутбуков'},
        ]

        for type_data in types:
            DeviceType.objects.create(
                name=type_data['name'],
                description=type_data['description']
            )
        self.stdout.write('Созданы типы оборудования')

    def create_employees(self):
        """Создаём сотрудников"""
        employees = [
            {'full_name': 'Иванов Иван Иванович', 'position': 'Разработчик Python', 'department': 'Backend',
             'email': 'i.ivanov@company.ru'},
            {'full_name': 'Петрова Анна Сергеевна', 'position': 'Тестировщик', 'department': 'QA',
             'email': 'a.petrova@company.ru'},
            {'full_name': 'Сидоров Сергей Михайлович', 'position': 'Data Engineer', 'department': 'Analytics',
             'email': 's.sidorov@company.ru'},
            {'full_name': 'Козлова Мария Дмитриевна', 'position': 'Frontend разработчик', 'department': 'Frontend',
             'email': 'm.kozlova@company.ru'},
            {'full_name': 'Николаев Алексей Петрович', 'position': 'DevOps инженер', 'department': 'Infrastructure',
             'email': 'a.nikolaev@company.ru'},
        ]

        for emp_data in employees:
            Employee.objects.create(
                full_name=emp_data['full_name'],
                position=emp_data['position'],
                department=emp_data['department'],
                email=emp_data['email']
            )
        self.stdout.write('Созданы сотрудники')

    def create_devices(self):
        """Создаём оборудование"""
        devices = [
            {'inventory_number': 'NB001', 'model': 'Dell Latitude 5520', 'type': 'Ноутбук', 'status': 'available'},
            {'inventory_number': 'NB002', 'model': 'Lenovo ThinkPad T14', 'type': 'Ноутбук', 'status': 'in_use'},
            {'inventory_number': 'NB003', 'model': 'MacBook Pro 16', 'type': 'Ноутбук', 'status': 'broken'},
            {'inventory_number': 'MON001', 'model': 'Samsung S24R350', 'type': 'Монитор', 'status': 'available'},
            {'inventory_number': 'MON002', 'model': 'Dell U2720Q', 'type': 'Монитор', 'status': 'in_use'},
            {'inventory_number': 'MSE001', 'model': 'Logitech MX Master 3', 'type': 'Мышь', 'status': 'available'},
            {'inventory_number': 'KBD001', 'model': 'Keychron K2', 'type': 'Клавиатура', 'status': 'available'},
            {'inventory_number': 'DOC001', 'model': 'Dell WD19', 'type': 'Док-станция', 'status': 'in_use'},
        ]

        for device_data in devices:
            device_type = DeviceType.objects.get(name=device_data['type'])
            Device.objects.create(
                inventory_number=device_data['inventory_number'],
                model=device_data['model'],
                device_type=device_type,
                status=device_data['status']
            )
        self.stdout.write('Создано оборудование')

    def create_requests(self):
        """Создаём заявки"""
        requests_data = [
            {'employee_email': 'i.ivanov@company.ru', 'device_number': 'NB002', 'status': 'approved',
             'purpose': 'Для разработки нового API'},
            {'employee_email': 'a.petrova@company.ru', 'device_number': 'MON002', 'status': 'approved',
             'purpose': 'Для тестирования интерфейса'},
            {'employee_email': 's.sidorov@company.ru', 'device_number': 'DOC001', 'status': 'approved',
             'purpose': 'Для работы с базами данных'},
            {'employee_email': 'm.kozlova@company.ru', 'device_number': 'NB001', 'status': 'pending',
             'purpose': 'Для разработки React компонентов'},
        ]

        for req_data in requests_data:
            employee = Employee.objects.get(email=req_data['employee_email'])
            device = Device.objects.get(inventory_number=req_data['device_number'])

            Request.objects.create(
                employee=employee,
                device=device,
                status=req_data['status'],
                purpose=req_data['purpose']
            )
        self.stdout.write('Созданы заявки')

    def create_repairs(self):
        """Создаём ремонты"""
        repairs_data = [
            {'device_number': 'NB003', 'reported_by_email': 'i.ivanov@company.ru',
             'description': 'Не включается, не реагирует на кнопку питания'},
        ]

        for repair_data in repairs_data:
            device = Device.objects.get(inventory_number=repair_data['device_number'])
            employee = Employee.objects.get(email=repair_data['reported_by_email'])

            Repair.objects.create(
                device=device,
                reported_by=employee,
                description=repair_data['description'],
                status=Repair.STATUS_REPAIRING
            )
        self.stdout.write('Созданы ремонты')

    def create_users_with_roles(self):
        """Создаём пользователей и связываем с сотрудниками"""
        users_data = [
            {'username': 'admin', 'email': 'admin@company.ru', 'role': 'admin', 'password': '1111',
             'employee_email': None},
            {'username': 'tech', 'email': 'tech@company.ru', 'role': 'tech', 'password': '1111',
             'employee_email': None},
            {'username': 'analyst', 'email': 'analyst@company.ru', 'role': 'analyst', 'password': '1111',
             'employee_email': None},
            {'username': 'ivanov', 'email': 'i.ivanov@company.ru', 'role': 'employee', 'password': '1111',
             'employee_email': 'i.ivanov@company.ru'},
            {'username': 'petrova', 'email': 'a.petrova@company.ru', 'role': 'employee', 'password': '1111',
             'employee_email': 'a.petrova@company.ru'},
            {'username': 'sidorov', 'email': 's.sidorov@company.ru', 'role': 'employee', 'password': '1111',
             'employee_email': 's.sidorov@company.ru'},
            {'username': 'kozlova', 'email': 'm.kozlova@company.ru', 'role': 'employee', 'password': '1111',
             'employee_email': 'm.kozlova@company.ru'},
            {'username': 'nikolaev', 'email': 'a.nikolaev@company.ru', 'role': 'employee', 'password': '1111',
             'employee_email': 'a.nikolaev@company.ru'},
        ]

        for user_data in users_data:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )

            UserProfile.objects.create(
                user=user,
                role=user_data['role']
            )

            if user_data['employee_email']:
                employee = Employee.objects.get(email=user_data['employee_email'])
                employee.user = user
                employee.save()
                self.stdout.write(f"Связали {user.username} с {employee.full_name}")

        self.stdout.write('Созданы пользователи')