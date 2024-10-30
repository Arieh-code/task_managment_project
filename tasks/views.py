from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Task, CompletedTaskHistory
from .forms import TaskForm 
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
# Create your views here.


def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})


def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            if task.completed:
                CompletedTaskHistory.objects.create(task=task, completed_date=timezone.now())
                print("Task completed on creation:", task.title)
        return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})
    
    
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            if not task.completed and form.cleaned_data['completed']:
                CompletedTaskHistory.objects.create(task=task, completed_date=timezone.now())
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})


def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_delete.html', {'task': task})



def completed_task_history(request):
    history=(
        CompletedTaskHistory.objects
        .annotate(month=TruncMonth('completed_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    return render(request, 'tasks/completed_task_history.html', {'history': history})