from django.urls import path
from . import views


urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('update/<int:pk>/', views.task_update, name='task_update'),
    path('delete/<int:pk>/', views.task_delete, name='task_delete'),
    path('history/', views.completed_task_history, name='completed_task_history'),
    path("profile-setup/", views.profile_setup, name="profile_setup"),
    
]
