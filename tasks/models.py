from django.db import models
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
        # automatically set end date based on the importance if not specified
        if not self.end_date:
            if self.importance == 'Low':
                self.end_date = timezone.now() + timezone.timedelta(days=30)
                logger.debug(f"Set end date to {self.end_date} for low priority task.")
            elif self.importance =='Medium':
                self.end_date = timezone.now() + timezone.timedelta(days=14)
                logger.debug(f"Set end date to {self.end_date} for medium priority task.")
            elif self.importance == 'Urgent':
                self.end_date = timezone.now() + timezone.timedelta(days=3)
                logger.debug(f"Set end date to {self.end_date} for high priority task.")
        
        logger.info(f"Saving task '{self.title}' with end date set to: {self.end_date}")
        super().save(*args, **kwargs)

    
    
    def __str__(self):
        return self.title  # This returns the title of the task when you print the Task object


class CompletedTaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)  # Link to the Task model
    completed_date = models.DateTimeField(default=timezone.now) # Timestamp for when the task was
    
    
    def __str__(self):
        return f"completed: {self.task.title} on {self.completed_date}"
    