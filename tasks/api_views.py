# tasks/api_views.py

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task, CompletedTaskHistory
from .serializers import TaskSerializer, CompletedTaskHistorySerializer  # You'll need to create a serializer
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger('api')

class TaskListView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

    def get(self, request):
        logger.info(f"Received request for task list by user: {request.user.username}" )
        tasks = Task.objects.filter(user=request.user)  # Get tasks for the logged-in user
        serializer = TaskSerializer(tasks, many=True)
        logger.info(f"Returned {tasks.count()} tasks for {request.user.username}")
        return Response(serializer.data, status=status.HTTP_200_OK)



class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users
    
    
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the task with the logged-in user
            logger.info(f"Task {request.data.get('title')} created by user: {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class TaskUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users
    
    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Task {request.data.get('title')} updated by user: {request.user.username}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class TaskDeleteView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.delete()
        logger.info(f"Task '{request.data.get('title')}' deleted by: {request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    

class CompletedTaskHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        logger.info(f"Received request for completed tasks by user {request.user.username}"
                    f"with filters: Month - {month}, Year - {year}")
        
        completed_tasks = CompletedTaskHistory.objects.filter(task__user = request.user)
        
        if year:
            completed_tasks = completed_tasks.filter(completed_date__year = year)
        if month:
            completed_tasks = completed_tasks.filter(completed_date__month = month)
        
        
        serializer = CompletedTaskHistorySerializer(completed_tasks, many=True)
        
        logger.info(f"Returned {completed_tasks.count()} completed tasks for user: {request.user.username}")
        return Response(serializer.data, status=status.HTTP_200_OK)