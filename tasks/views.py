from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Task, CompletedTaskHistory
from .forms import TaskForm 
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required




# Create your views here.

# Apply login_required to the task_list view

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            print("Task 'completed' status on creation:", task.completed)
            task.user = request.user
            task.save()
            
            if task.completed:
                CompletedTaskHistory.objects.create(task=task, completed_date=timezone.now())
                print("Task completed on creation:", task.title)  # Check if this prints correctly
        return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})
    
    
@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    previous_completed_status = task.completed
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        
        if form.is_valid():
            # Capture the initial `completed` state before saving
            # previous_completed_status = task.completed
            task = form.save(commit=False)
            task.user = request.user
            task.save()

            # Add to history if transitioning to `completed`
            if not previous_completed_status and task.completed:
                CompletedTaskHistory.objects.create(task=task, completed_date=timezone.now())
                print(f"Completed history entry created for task: {task.title}")

            return redirect('task_list')
    else:
        # Set initial data to match current task state
        form = TaskForm(instance=task, initial={'completed': task.completed})
        print("Initial 'completed' status set in form:", task.completed)

    return render(request, 'tasks/task_form.html', {'form': form})




@login_required  # Ensure that the user is logged in
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)  # Ensure the task belongs to the current user
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_delete.html', {'task': task})




@login_required
def completed_task_history(request):
    history = (
        CompletedTaskHistory.objects
        .filter(task__user=request.user)  # Make sure this filter is present
        .annotate(month=TruncMonth('completed_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    return render(request, 'tasks/completed_task_history.html', {'history': history})
