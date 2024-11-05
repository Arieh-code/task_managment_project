# tasks/api_urls.py
from django.urls import path
from . import api_views
from rest_framework_simplejwt.views import(
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('tasks/', api_views.TaskListView.as_view(), name='task_list_api'),
    path('tasks/create/', api_views.TaskCreateView.as_view(), name='task_create_api'),
    path('tasks/<int:pk>/update/', api_views.TaskUpdateView.as_view(), name='task_update_api'),
    path('tasks/<int:pk>/delete/', api_views.TaskDeleteView.as_view(), name='task_delete_api'),
    path('tasks/completed-history/', api_views.CompletedTaskHistoryView.as_view(), name='completed_task_history_api'),
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]
