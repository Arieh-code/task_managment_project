from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger('tasks')


# Create your models here.


class Task(models.Model):
    
    # set choices for the importance of a task
    IMPORTANCE_CHOICES = [
    ('Low', 'Low Priority (Complete within a month)'),
    ('Medium', 'Moderate Priority (Complete within two weeks)'),
    ('Urgent', 'High Priority (Complete within a few days)'),
    ]
    
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=200)  # Title of the task, max length 200 characters
    description = models.TextField(blank=True, null=True)  # Optional description of the task
    completed = models.BooleanField(default=False)  # Boolean flag indicating if the task is completed
    importance = models.CharField(max_length=10, choices=IMPORTANCE_CHOICES, default='low')
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the task was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for when the task was last updated
    end_date = models.DateTimeField(blank=True, null=True)
    
    

    def save(self, *args, **kwargs):
        # Check if task completion status has changed from the last saved state
        creating_history = self.pk is None or (not self.completed and self.completed)

        # Define the automatic end dates based on importance
        importance_days = {
            'Low': 30,
            'Medium': 14,
            'Urgent': 3
        }
        
        # Automatically set end date based on importance if not specified
        if not self.end_date:
            days_to_add = importance_days.get(self.importance)
            if days_to_add:
                self.end_date = timezone.now() + timezone.timedelta(days=days_to_add)
                logger.debug(f"Set end date to {self.end_date} for {self.importance} priority task.")
            else:
                raise ValidationError("Invalid importance level")
        
        logger.info(f"Saving task '{self.title}' with end date set to: {self.end_date}")
        
        # Save the task model instance
        super().save(*args, **kwargs)
        
        # Create history record if task has been marked as complete
        if creating_history and self.completed:
            CompletedTaskHistory.objects.get_or_create(task=self, completed_date=timezone.now())
            logger.info(f"Completed task history created for '{self.title}'.")


    
    
    def __str__(self):
        return self.title  # This returns the title of the task when you print the Task object


class CompletedTaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)  # Link to the Task model
    completed_date = models.DateTimeField(default=timezone.now) # Timestamp for when the task was
    
    
    def __str__(self):
        return f"completed: {self.task.title} on {self.completed_date}"
    