
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
        
        Task.objects.create(user=self.user, title='title1', description='first task')
        Task.objects.create(user=self.user, title='title2', description='second task')
        
        url = reverse('task_list_api')
        
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    
    
    
    def test_task_update(self):
        ''' Testing update using API'''
        
        task = Task.objects.create(user=self.user, title='initial task', description='to be updated')
        url = reverse('task_update_api', args=[task.pk])
        data = {'title': 'task update'}
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('title'), 'task update')
        
    
    def test_delete(self):
        ''' Testing delete using API '''
        
        task = Task.objects.create(user=self.user, title='task to delete', description='to be deleted')
        url = reverse('task_delete_api', args=[task.pk])
        
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
        
    
    def test_completed_task_history(self):
        ''' Testing fetching completed tasks history with filters'''
        # Create a task and mark it as complete
        task = Task.objects.create(
            user=self.user,
            title="Completed Task",
            description="This task is completed",
            completed=True,
            importance="Medium"
        )
        CompletedTaskHistory.objects.create(task=task, completed_date=timezone.now())
        
        # Define default month and year for filtering
        current_date = timezone.now()
        month = current_date.month
        year = current_date.year
        url = reverse('completed_task_history_api')
        # Request completed tasks history with month and year filter
        response = self.client.get(url, format='json')
        
        # Assert successful response and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        