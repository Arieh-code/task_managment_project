from django.db import models

# Create your models here.


class Task(models.Model):
    title = models.CharField(max_length=200)  # Title of the task, max length 200 characters
    description = models.TextField(blank=True, null=True)  # Optional description of the task
    completed = models.BooleanField(default=False)  # Boolean flag indicating if the task is completed
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the task was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the task was last updated

    def __str__(self):
        return self.title  # This returns the title of the task when you print the Task object
