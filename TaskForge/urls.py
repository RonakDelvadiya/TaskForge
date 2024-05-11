from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", admin.site.urls),
    path("task-management/", include('task_management.urls')),
]