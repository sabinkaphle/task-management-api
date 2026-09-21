from rest_framework.decorators import api_view, permission_classes
from apps.tasks.models import Task
from rest_framework.permissions import IsAuthenticated
from apps.tasks.api.serializer import (
    TaskSerializer,
    TaskApiSerializer,
    TaskUpdateSerializer,
    TaskCreateSerializer,
    TaskResponseSeerializer,
    TaskEmptyResponseSerializer
)
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from datetime import date

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse


@extend_schema(
    summary="Create a task",
    description="Create a new task. The authenticated user becomes the task creator. A task starts with TODO status.",
    request=TaskCreateSerializer,
    responses={
        201: TaskResponseSeerializer,
        400: None,
        401: None,
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_task(requests):
    data = requests.data
    user = requests.user
    serializer = TaskSerializer(data=data)

    if serializer.is_valid():
        serializer.save(created_by=user)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@extend_schema(
    summary="List your tasks",
    description="Returns tasks where the authenticated user is either the creator or the assignee. Supports filtering by status, creator, assignee, overdue, and completion.",
    parameters=[
        OpenApiParameter(
            name="status",
            description="Filter tasks by status.",
            required=False,
            type=str,
            enum=["todo", "in_progress", "completed"],
        ),
        OpenApiParameter(
            name="created_by_me",
            description="Show only tasks created by you.",
            required=False,
            type=bool,
        ),
        OpenApiParameter(
            name="assigned_to_me",
            description="Show only tasks assigned to you.",
            required=False,
            type=bool,
        ),
        OpenApiParameter(
            name="over_due",
            description="Show tasks that are past their due date and not completed.",
            required=False,
            type=bool,
        ),
        OpenApiParameter(
            name="completed",
            description="Show only completed tasks.",
            required=False,
            type=bool,
        ),
    ],
    responses={
    200: OpenApiResponse(
        response=TaskResponseSeerializer(many=True),
        description="List of tasks. If no tasks are available, the response contains a message."
    ),
    401: None,
}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_tasks(requests):
    today_date = date.today()
    user = requests.user

    task_status = requests.query_params.get("status")
    created_by_me = requests.query_params.get("created_by_me")
    assigned_to_me = requests.query_params.get("assigned_to_me")
    over_due = requests.query_params.get("over_due")
    completed_tasks = requests.query_params.get("completed")

    tasks = Task.objects.filter(
        Q(created_by=user) | Q(assigned_to=user)
    )

    if task_status:
        tasks = tasks.filter(status=task_status)

    if created_by_me == "true":
        tasks = tasks.filter(created_by=user)

    if assigned_to_me == "true":
        tasks = tasks.filter(assigned_to=user)

    if over_due == "true":
        tasks = tasks.filter(due_date__lt=today_date)
        tasks = tasks.exclude(status="completed")

    if completed_tasks == "true":
        tasks = tasks.filter(status="completed")

    if not tasks.exists():
        return Response({
            "message": "You have no tasks."
        })

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Get task details",
    description="Retrieve a task if the authenticated user is either its creator or assignee.",
    responses={
        200: TaskSerializer,
        401: None,
        403: None,
        404: None,
    }
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def task_details(requests, id):
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        return Response(
            {"message": "Task not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if task.created_by == requests.user or task.assigned_to == requests.user:
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    else:
        return Response(
            {"message": "You do not have permission to access this task."},
            status=status.HTTP_403_FORBIDDEN
        )


@extend_schema(
    summary="Update task details",
    description="Update task details such as title, description, due date, or assignee. Only the task creator can perform this operation. Status cannot be changed here.",
    request=TaskUpdateSerializer,
    responses={
        200: TaskSerializer,
        400: None,
        401: None,
        403: None,
        404: None,
    }
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_task(requests, id):
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        return Response(
            {"message": "Task not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if task.created_by == requests.user:
        serializer = TaskSerializer(
            task,
            data=requests.data,
            partial=True,
            context={"update_type": "details"}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    else:
        return Response(
            {"message": "You do not have permission to access this task."},
            status=status.HTTP_403_FORBIDDEN
        )


@extend_schema(
    summary="Delete a task",
    description="Delete a task. Only the task creator can delete the task.",
    responses={
        204: None,
        401: None,
        403: None,
        404: None,
    }
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete(requests, id):
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        return Response(
            {"message": "Task not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if task.created_by == requests.user:
        task.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    else:
        return Response(
            {"message": "You do not have permission to access this task."},
            status=status.HTTP_403_FORBIDDEN
        )


@extend_schema(
    summary="Update task status",
    description="Change the status of a task. Only the assigned user can change the task status.",
    request=TaskApiSerializer,
    responses={
        200: TaskSerializer,
        400: None,
        401: None,
        403: None,
        404: None,
    }
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_status(requests, id):
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        return Response(
            {"message": "Task not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if task.assigned_to == requests.user:
        updated_status = requests.data.get("status")

        data = {
            "status": updated_status
        }

        serializer = TaskSerializer(
            task,
            data=data,
            partial=True,
            context={"update_type": "status"}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    else:
        return Response(
            {"message": "You do not have permission to access this task."},
            status=status.HTTP_403_FORBIDDEN
        )