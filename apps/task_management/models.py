from django.db import models
from users.models import UserProfile

"""
Model to manage most common fields. 
By inheriting this model mentioned field will be added automatically.
"""
class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class TaskManage(BaseModel):
    COMPLAINTS_TYPE = [
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('portal', 'Portal'),
        ("other", "Other")
    ]

    TASK_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
    ]

    COMPLETION_REASON = [
        ("resolved_successfully",  "Resolved Successfully"),
        ("incomplete_information",  "Incomplete Information"),
        ("parts_equipment_needed",  "Parts/Equipment Needed"),
        ("client_unavailable",  "Client Unavailable"),
        ("not_serviceable",  "Not Serviceable"),
        ("out_of_scope",  "Out of Scope"),
        ("duplicate_task",  "Duplicate Task"),
        ("technical_limitation",  "Technical Limitation"),
        ("client_requested_delay",  "Client-Requested Delay")
    ]

    title = models.CharField(max_length=100, db_index=True)
    task_status = models.CharField(max_length=20, choices=TASK_STATUS, db_index=True, default='pending') 
    description = models.TextField(blank=True, null=True)
    priority = models.PositiveBigIntegerField(default=1) # Added as an int field because its easy to sort by this field. 
    severity = models.PositiveBigIntegerField(default=1) # Added as an int field because its easy to sort by this field.
    deadline = models.DateField(db_index=True)
    assignee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tasks_assigned_to')
    assignee_note = models.TextField(blank=True, null=True)
    manager = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='tasks_assigned_by')
    complaints_received_via = models.CharField(max_length=10, choices=COMPLAINTS_TYPE, blank=True, null=True)
    completion_reason = models.CharField(max_length=100, blank=True, null=True, db_index=True, choices=COMPLETION_REASON) # We can add another model for reason if it is frequently changing.
    completion_date = models.DateField(db_index=True, blank=True, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        # app_label = 'task_management_model'
        ordering = ("priority", "severity", "-deadline",) # Default behaviour of listing of this model.
    
    @classmethod # it can be use explicitly, This is for example I have added only, in code it is not used anywhere.
    def get_tasks(cls, status=None, assignee=None, manager=None, is_active=True):
        queryset = cls.objects.filter(is_active=is_active)
        if status:
            queryset = queryset.filter(task_status=status)
        if assignee:
            queryset = queryset.filter(assignee=assignee)
        if manager:
            queryset = queryset.filter(manager=manager)
        return queryset

