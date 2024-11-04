from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Task, CompletedTaskHistory
from .forms import TaskForm 
from django.utils import timezone
from django.db.models import Count, F
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from datetime import datetime
import logging

logger = logging.getLogger('tasks')



# Create your views here.

# Apply login_required to the task_list view

@login_required
def task_list(request):
    tasks = get_user_task(request.user).filter(completed=False)
    filter_importance = request.GET.get('importance')
    sort_by = request.GET.get('sort')
    
    if filter_importance:
        tasks = tasks.filter(importance=filter_importance)
        
    if sort_by == 'end_date':
        tasks = tasks.order_by('end_date')
    elif sort_by == 'importance':
        tasks = tasks.order_by('-importance')
        
    return render(request, 'tasks/task_list.html', 
                  {'tasks': tasks,
                   'filter_importance': filter_importance,
                   'sort_by': sort_by,
                   })




@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            
            logger.info(f"Task '{task.title}' created by user {task.user.username}.")
            
            if task.completed:
                CompletedTaskHistory.objects.create(task=task, completed_date=timezone.now())
                logger.info(f"Task '{task.title}' marked as complete upon creation.")
                
        return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})
    
    
@login_required
def task_update(request, pk):
    task = get_user_task(request.user, pk=pk)
    previous_completed_status = task.completed
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        
        if form.is_valid():

            task = form.save(commit=False)
            task.user = request.user
            task.save()
            
            logger.info(f"Task updated successfully by user: {task.user.username}.")

            # Add to history if transitioning to `completed`
            if not previous_completed_status and task.completed:
                CompletedTaskHistory.objects.create(task=task, completed_date=timezone.now())
                logger.info(f"Task '{task.title}' marked as complete by user: {task.user.username}.")
                
            # Remove from history if transitioning from `completed` to `not completed`
            elif previous_completed_status and not task.completed:
                CompletedTaskHistory.objects.filter(task=task).delete()
                logger.info(f"Task '{task.title}' marked as not completed by user: {task.user.username}.")
                
            return redirect('task_list')
    else:
        # Set initial data to match current task state
        form = TaskForm(instance=task, initial={'completed': task.completed})

    return render(request, 'tasks/task_form.html', {'form': form})




@login_required  # Ensure that the user is logged in
def task_delete(request, pk):
    task = get_user_task(request.user, pk=pk)  # Ensure the task belongs to the current user
    if request.method == 'POST':
        task.delete()
        logger.info(f"Task '{task.title}' (ID: {pk}) deleted by user '{request.user.username}'.")
        return redirect('task_list')
    return render(request, 'tasks/task_delete.html', {'task': task})




@login_required
def completed_task_history(request):
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    importance = request.GET.get('importance', '')
    
    # filter the completed task history for the selected month
    completed_tasks = CompletedTaskHistory.objects.filter(
        task__user = request.user,
        completed_date__year = year,
        completed_date__month = month,
    ).annotate(
        title = F('task__title'),
        description = F('task__description'),
        importance = F('task__importance'),

    )
    
    if importance:
        completed_tasks = completed_tasks.filter(task__importance=importance)
    
    importance_order = {'Urgent':1, 'Medium':2, 'Easy':3}
    
    completed_tasks = sorted(
        completed_tasks, 
        key= lambda x: importance_order.get(x.importance, 4)
        )
    
    months = [(i, datetime(2024, i, 1).strftime('%B')) for i in range(1, 13)]
    years = range(timezone.now().year-5, timezone.now().year+1)
    
    return render(request, 'tasks/completed_task_history.html', {
        'completed_tasks' : completed_tasks,
        'months' : months,
        'years' : years,
        'selected_month' : month,
        'selected_year': year,
        'importance_levels' : ['Urgent', 'Medium', 'Low'],
        'importance' : importance
        })

def get_user_task(user, pk=None):
    if pk:
        return get_object_or_404(Task, pk=pk, user=user)
    return Task.objects.filter(user=user)