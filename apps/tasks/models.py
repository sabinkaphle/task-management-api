from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Status(models.TextChoices):
    TODO = "todo", "TODO"
    IN_PROGRESS = "in_progress", " In Progress"
    COMPLETED = "completed", "Completed"

class Task(models.Model):
    title = models.CharField(max_length=100, help_text="task title")
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_tasks")
    assigned_to = models.ForeignKey(User, models.SET_NULL, related_name="assigned_tasks", null=True)
    status = models.CharField(max_length=20 ,choices=Status.choices, default=Status.TODO)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "tasks"