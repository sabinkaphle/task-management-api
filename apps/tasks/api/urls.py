from django.urls import path
from apps.tasks.api.views import create_task, list_tasks, task_details, update_status, update_task,delete

urlpatterns = [
    path("create/",create_task),
    path("list/", list_tasks),
    path("list/<int:id>/", task_details),
    path("update/<int:id>/", update_task),
    path("delete/<int:id>/", delete),
    path("update-status/<int:id>/", update_status)
]