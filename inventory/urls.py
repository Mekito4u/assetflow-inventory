from django.urls import path
from . import views

urlpatterns = [
    path('', views.device_list, name='device_list'),
    path('employee/<int:employee_id>/', views.employee_devices, name='employee_devices'),
]