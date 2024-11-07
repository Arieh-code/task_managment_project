
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from tasks.models import Task, CompletedTaskHistory

class TaskAPITestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        
        
    def test_task_create(self):
        ''' Testing creating a task via API request '''
        
        url = reverse('task_create_api')
        data = {
            'title' : 'test task',
            'description' : 'Testing task creating API',
            'completed' : False,
            'importance' : 'Urgent'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('title'), 'test task')
        self.assertEqual(response.data.get('importance'), 'Urgent')
        
        
    def test_task_list(self):
        ''' Testing listing the tasks of authenticated users'''
        
        Task.objects.create(user=self.user, title='title1', description='first task', importance='Medium')
        Task.objects.create(user=self.user, title='title2', description='second task', importance='Low')
        
        url = reverse('task_list_api')
        
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    
    
    
    def test_task_update(self):
        ''' Testing update using API'''
        
        task = Task.objects.create(user=self.user, title='initial task', description='to be updated', importance='Urgent')
        url = reverse('task_update_api', args=[task.pk])
        data = {'title': 'task update'}
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), 'task update')
        
    
    def test_delete(self):
        ''' Testing delete using API '''
        
        task = Task.objects.create(user=self.user, title='task to delete', description='to be deleted', importance='Low')
        url = reverse('task_delete_api', args=[task.pk])
        
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
        
    




class CompletedTaskHistoryViewTest(APITestCase):

    def setUp(self):
        # Setup user and client with JWT
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Create and mark a task as complete, adding it to the completed history
        self.task = Task.objects.create(
            user=self.user,
            title="Initial Test Task",
            description="This is a test task",
            completed=True,
            importance="Medium"
        )
        CompletedTaskHistory.objects.create(
            task=self.task,
            completed_date=timezone.now()
        )

    def test_task_creation_and_completion(self):
        """Test creating a task and ensuring it enters completed history when marked complete"""
        # Create a new task
        task = Task.objects.create(
            user=self.user,
            title="New Task to Complete",
            description="A new test task to be completed",
            completed=False,
            importance="Low"
        )
        
        # Mark the task as complete
        task.completed = True
        task.save()

        # Check that completed history now has two entries
        self.assertEqual(CompletedTaskHistory.objects.filter(task__user=self.user).count(), 2)

    def test_completed_task_history_api(self):
        """Test fetching completed tasks history from the API with month and year filters"""
        current_month = timezone.now().month
        current_year = timezone.now().year
        url = reverse('completed_task_history_api')  # Correct API endpoint name

        # Fetch completed history without filters to confirm both entries
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Confirm two entries in completed history

        # Fetch completed history with month and year filters
        response = self.client.get(url, {'month': current_month, 'year': current_year})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # Confirm filtered result based on month and year

    def test_completed_task_history_invalid_params(self):
        """Test invalid month and year parameters"""
        url = reverse('completed_task_history_api')
        
        # Invalid month test
        response = self.client.get(url, {'month': 13})  # Invalid month
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid year test
        response = self.client.get(url, {'year': 'abcd'})  # Invalid year
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

