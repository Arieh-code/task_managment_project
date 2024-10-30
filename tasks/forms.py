from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed']  # Include the fields you want users to fill out

    # Optional: Add custom validation or other methods here if needed
