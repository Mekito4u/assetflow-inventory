from django.core.management.base import BaseCommand
from inventory.models import DeviceType, Employee, Device, Request


class Command(BaseCommand):
    help = 'Очищает все данные (кроме пользователей)'

    def handle(self, *args, **options):
        Request.objects.all().delete()
        Device.objects.all().delete()
        Employee.objects.all().delete()
        DeviceType.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('✅ Все данные очищены!'))