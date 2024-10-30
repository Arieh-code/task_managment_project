from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.


class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)  # Title of the task, max length 200 characters
    description = models.TextField(blank=True, null=True)  # Optional description of the task
    completed = models.BooleanField(default=False)  # Boolean flag indicating if the task is completed
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the task was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the task was last updated

    def __str__(self):
        return self.title  # This returns the title of the task when you print the Task object


class CompletedTaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)  # Link to the Task model
    completed_date = models.DateTimeField(default=timezone.now) # Timestamp for when the task was
    
    
    def __str__(self):
        return f"completed: {self.task.title} on {self.completed_date}"
    