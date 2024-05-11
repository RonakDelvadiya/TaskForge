from django.contrib import admin
from .models import TaskManage

class TaskManageAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_status', 'priority', 'severity', 'deadline', 'assignee', 'manager', "created_on", "updated_on")
    list_filter = ('task_status', 'priority', 'severity', 'deadline', 'assignee', 'manager', 'complaints_received_via')
    search_fields = ('title', 'description', 'assignee__username', 'manager__username')
    ordering = ("priority", "severity", '-deadline',)  # Default ordering by deadline (descending)

admin.site.register(TaskManage, TaskManageAdmin)
