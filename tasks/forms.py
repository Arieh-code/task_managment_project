from django import forms
from .models import Task
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed', 'importance', 'end_date']  # Include the fields you want users to fill out

        
    # Optional: Add custom validation or other methods here if needed
    end_date = forms.DateField(
        required=False,
        widget=forms.SelectDateWidget,
        help_text="Leave empty to auto assign based on importance level"
    )



class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]