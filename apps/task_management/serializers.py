from rest_framework import serializers
from .models import TaskManage
from users.models import UserProfile


class UserProfileMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id","first_name","last_name","role") # For data abstraction, removed other fields.


class ListTaskManageSerializer(serializers.ModelSerializer):
    assignee = UserProfileMetaDataSerializer() # Append assignee's metadata to display.
    manager = UserProfileMetaDataSerializer() # Append manager's metadata to display.
    class Meta:
        model = TaskManage
        fields = '__all__'

"""
This ser. will be used to add/update full task except below fields.
Exception(can not add/update assignee's fields) : 'assignee_note', 'task_status', 'completion_reason', "completion_date"
"""
class AddUpdateTaskManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskManage
        fields = ("title", "task_status", "description", "priority", "severity", "deadline", "assignee", "manager", "complaints_received_via", "completion_date", "is_active", "created_on", "updated_on")


"""
This ser. will be used to update below fields only, because other fields are managed by Manager/Admin only.
Required field for Worker role : 'assignee_note', 'task_status', 'completion_reason', "completion_date"
"""
class UpdateTaskManageForWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskManage
        fields = ('assignee_note', 'task_status', 'completion_reason', "completion_date")