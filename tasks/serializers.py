# tasks/serializers.py

from rest_framework import serializers
from .models import Task, CompletedTaskHistory

class TaskSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)  # Display the username
    importance_display = serializers.CharField(source='get_importance_display', read_only=True)  # Importance label

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completed', 'importance', 'importance_display', 
            'end_date', 'created_at', 'updated_at', 'user'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user', 'importance_display']


class CompletedTaskHistorySerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_importance = serializers.CharField(source='task.importance', read_only=True)
    task_completed_date = serializers.DateTimeField(source='completed_date')

    class Meta:
        model = CompletedTaskHistory
        fields = ['id', 'task_title', 'task_importance', 'task_completed_date']