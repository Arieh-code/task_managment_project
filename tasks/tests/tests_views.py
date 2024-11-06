from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from ..models import Task, CompletedTaskHistory
from django.contrib.auth.models import User

# Create your tests here.

class TaskTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testUser', password='testPassword')
        self.client.login(username='testUser', password='testPassword')
        
    def test_task_creation(self):
        '''Test that the task is created with the correct fields, including the calculated end_date'''
        task = Task.objects.create(
            user=self.user,  # Use lowercase 'user' to match the model field
            title='Test Task Create',
            description='This is a simple test task',
            completed=False,
            importance='Urgent'
        )
        
        self.assertIsNotNone(task.end_date)  # Check that end_date is automatically set
        self.assertEqual(
            task.end_date.date(), 
            (timezone.now() + timezone.timedelta(days=3)).date()
        )
        
    def test_task_completion(self):
        '''Test marking a task as completed and ensure it is recorded in history'''
        
        # Create the task without marking it completed
        task = Task.objects.create(
            user=self.user,
            title='Test Task Complete',
            description='A task to test completion',
            completed=False,
            importance='Low'
        )
        
        # Update the task to completed and save
        task.completed = True
        task.save()
        
        # Reload from database to confirm changes
        task.refresh_from_db()
        
        # Check that the task completion is recorded in history
        history = CompletedTaskHistory.objects.filter(task=task)
        self.assertEqual(history.count(), 1)  # Ensure one record in history
        self.assertEqual(history.first().task, task)

    def test_completed_task_history_view(self):
        """Test accessing the completed task history page with filtering."""
        task = Task.objects.create(
            user=self.user,
            title="History Test Task",
            description="A task to test history view",
            completed=True,
            importance="Medium"
        )
        CompletedTaskHistory.objects.create(task=task, completed_date=timezone.now())

        # Access completed task history page
        response = self.client.get(reverse('completed_task_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "History Test Task")
        self.assertContains(response, "Importance: Medium")
