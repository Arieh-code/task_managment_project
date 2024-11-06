# tasks/api_views.py

from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task, CompletedTaskHistory
from .serializers import TaskSerializer, CompletedTaskHistorySerializer  # You'll need to create a serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
import logging

logger = logging.getLogger('api')

class TaskListView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

    def get(self, request):
        try:
            logger.info(f"Received request for task list by user: {request.user.username}" )
            tasks = Task.objects.filter(user=request.user)  # Get tasks for the logged-in user
            if not tasks.exists():
                logger.warning(f"No tasks found for user: {request.user.username}")            
            serializer = TaskSerializer(tasks, many=True)
            logger.info(f"Returned {tasks.count()} tasks for {request.user.username}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except APIException as e:
            logger.error(f"APIException occurred for user: {request.user.username} while fetching task list: {str(e)}")
            return Response({"error": "an error occurred while fetching task list"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Unexpected error for user: {request.user.username} while fetching task list: {str(e)}")
            return Response({"error": "an unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users


    def post(self, request):
        try:   
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)  # Associate the task with the logged-in user
                logger.info(f"Task {request.data.get('title')} created by user: {request.user.username}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Invalid data for task create by user: {request.user.username} - Errors {serializer.errors}")
                raise ValidationError(serializer.errors)

        except ValidationError as e:
            return Response({"error": "Invalid data", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"An unexpected error occurred for user {request.user.username} creating a new task: {str(e)}")
            return Response({"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

class TaskUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users
    
    def put(self, request, pk):
        try:
            
            task = get_object_or_404(Task, pk=pk, user=request.user)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Task {request.data.get('title')} updated by user: {request.user.username}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Invalid data for task update by user: {request.user.username}")
                raise ValidationError(serializer.errors)
        
        except ValidationError as e:
            return Response({"error": "Invalid data", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Task.DoesNotExist:
            logger.error(f"Task with id {pk} not found for user: {request.user.username}")
            return Response({"error": "Task not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"An unexpected error occurred for user {request.user.username} updating the task {pk}: {str(e)}")
            return Response({"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
    

class TaskDeleteView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        try:     
            task = get_object_or_404(Task, pk=pk, user=request.user)
            task.delete()
            logger.info(f"Task '{request.data.get('title')}' deleted by: {request.user.username}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Task.DoesNotExist:
            logger.error(f"Task with id {pk} not found for user: {request.user.username}")
            return Response({"error": "Task not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"An unexpected error occurred for user {request.user.username} deleting the task {pk}: {str(e)}")
            return Response({"error": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # Return a 500 Internal Server Error if an error occurs. This will help to debug the issue.
    
    

class CompletedTaskHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        logger.info(f"Received request for completed tasks by user {request.user.username}"
                    f"with filters: Month - {month}, Year - {year}")
        try:
            if month and not (1 <= month <= 12):
                raise ValidationError(f"Invalid month parameters: {month}")
            
            if year and len(year) > 4 or not year.isdigit():
                raise ValidationError(f"Invalid year parameters: {year}")
        
        except ValidationError as ve:
            logger.warning(f"Validation error in completed task history for user: {request.user.username}: {str(ve)}")
            return Response({"error": "validation error"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error validation parameters for user: {request.user.username}: {str(e)}")
            return Response({"error": "invalid parameters"}, status=status.HTTP_400_BAD_REQUEST)
                
        try:
            
            completed_tasks = CompletedTaskHistory.objects.filter(task__user = request.user)
            
            if year:
                completed_tasks = completed_tasks.filter(completed_date__year = year)
            if month:
                completed_tasks = completed_tasks.filter(completed_date__month = month)
            
            if not completed_tasks.exists():
                logger.warning(f"No completed tasks found of user: {request.user.username}"
                               f"With filters: Month - {month}, year - {year}")
                
            serializer = CompletedTaskHistorySerializer(completed_tasks, many=True)
            logger.info(f"Returned {completed_tasks.count()} completed tasks for user: {request.user.username}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Unexpected error retrieving completed tasks for user: {request.user.username}: {str(e)}")
            return Response({"error": "an error occurred while retrieving completed tasks"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)