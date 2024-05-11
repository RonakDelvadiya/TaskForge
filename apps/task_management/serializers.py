from rest_framework import serializers
from .models import TaskManage
from users.models import UserProfile


class UserProfileMetaDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id","first_name","last_name","role")


class ListTaskManageSerializer(serializers.ModelSerializer):
    assignee = UserProfileMetaDataSerializer()
    manager = UserProfileMetaDataSerializer()
    class Meta:
        model = TaskManage
        fields = '__all__'


class AddUpdateTaskManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskManage
        fields = ("title", "task_status", "description", "priority", "severity", "deadline", "assignee", "manager", "complaints_received_via", "completion_date", "is_active", "created_on", "updated_on")


class UpdateTaskManageForWorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskManage
        fields = ('assignee_note', 'task_status', 'completion_reason', "completion_date")