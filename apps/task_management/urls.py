from django.urls import path
from .views import TaskManageCrudOperation, WorkerTaskUpdate, TaskKPIs

urlpatterns = [
    path(r'task-manage-operation/', TaskManageCrudOperation.as_view(),name='task_manage_operation'),
    path(r'task-update-for-worker/', WorkerTaskUpdate.as_view(),name='task_update_for_worker'),
    path(r'task-kpis/', TaskKPIs.as_view(),name='task_kpis'),
]