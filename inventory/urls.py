from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.custom_login, name='login'),
    path('devices/', views.device_list, name='device_list'),
    path('employee/<int:employee_id>/', views.employee_devices, name='employee_devices'),
    path('request/create/<int:device_id>/', views.create_request, name='create_request'),
    path('requests/', views.manage_requests, name='manage_requests'),
    path('request/<int:request_id>/<str:new_status>/', views.update_request_status, name='update_request_status'),
    path('breakdown/<int:device_id>/', views.report_breakdown, name='report_breakdown'),
    path('extension/<int:request_id>/', views.request_extension, name='request_extension'),
    path('repairs/', views.repair_list, name='repair_list'),
    path('repair/<int:repair_id>/complete/', views.complete_repair, name='complete_repair'),
    path('reports/equipment/', views.equipment_report, name='equipment_report'),
    path('reports/breakdowns/', views.breakdown_statistics, name='breakdown_statistics'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('return/<int:request_id>/', views.return_device, name='return_device'),
]