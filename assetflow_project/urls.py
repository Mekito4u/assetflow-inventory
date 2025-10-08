from django.contrib import admin
from django.urls import path, include  # ← ДОБАВЬ include!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),  # ← ДОБАВЬ ЭТУ СТРОЧКУ!
]