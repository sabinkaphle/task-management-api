from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from apps.tasks.models import Task
from datetime import date

class TaskAPITests(APITestCase):
    def test_task_get(self):
        client = APIClient()
        response = client.get("/api/tasks/list/")

        assert response.status_code == 401

    def test_authenticated_user_can_list_tasks(self):
        user = User.objects.create_user(
            username="testuser",
            password="password123"
        )
        task = Task.objects.create(
            title = "Test task",
            created_by = user,
            due_date = date.today()
        )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/tasks/list/")

        assert len(response.data) == 1
        assert response.status_code == 200

    def test_authenticated_user_can_create_task(self):
        user = User.objects.create_user(
            username="creator",
            password="password123"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "title": "My first API task",
            "description": "Testing task creation",
            "due_date": "2026-09-20"
        }

        response = client.post("/api/tasks/create/", data)

        assert response.status_code == 201

    def test_authenticated_user_can_create_task(self):
        user = User.objects.create_user(
            username="creator",
            password="password123"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        data = {
            "title": "My first API task",
            "description": "Testing task creation",
            "due_date": "2026-09-20"
        }

        response = client.post("/api/tasks/create/", data)

        assert response.status_code == 201
        assert Task.objects.count() == 1

    def test_unauthenticated_user_cannot_create_task(self):
        client = APIClient()

        data = {
            "title": "Unauthorized task",
            "description": "This should not be created",
            "due_date": "2026-09-20"
        }

        response = client.post("/api/tasks/create/", data)

        assert response.status_code == 401
        assert Task.objects.count() == 0

    def test_creator_can_retrieve_own_task(self):
        user = User.objects.create_user(
            username="creator",
            password="password123"
        )

        task = Task.objects.create(
            title="My task",
            created_by=user,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/tasks/list/{task.id}/")

        assert response.status_code == 200

    def test_other_user_cannot_retrieve_task(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        other_user = User.objects.create_user(
            username="otheruser",
            password="password123"
        )

        task = Task.objects.create(
            title="Private task",
            created_by=creator,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=other_user)

        response = client.get(f"/api/tasks/list/{task.id}/")

        assert response.status_code == 403


    def test_assignee_can_retrieve_task(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        task = Task.objects.create(
            title="Assigned task",
            created_by=creator,
            assigned_to=assignee,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=assignee)

        response = client.get(f"/api/tasks/list/{task.id}/")

        assert response.status_code == 200

    def test_assignee_can_update_status(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        task = Task.objects.create(
            title="Assigned task",
            created_by=creator,
            assigned_to=assignee,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=assignee)

        data = {
            "status": "in_progress"
        }

        response = client.patch(
            f"/api/tasks/update-status/{task.id}/",
            data
        )

        assert response.status_code == 200

        task.refresh_from_db()
        assert task.status == "in_progress"

    def test_creator_cannot_update_status(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        task = Task.objects.create(
            title="Assigned task",
            created_by=creator,
            assigned_to=assignee,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=creator)

        data = {
            "status": "in_progress"
        }

        response = client.patch(
            f"/api/tasks/update-status/{task.id}/",
            data
        )

        assert response.status_code == 403

        task.refresh_from_db()
        assert task.status == "todo"

    def test_creator_can_update_task_details(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        task = Task.objects.create(
            title="Old title",
            description="Old description",
            created_by=creator,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=creator)

        data = {
            "title": "Updated title",
            "description": "Updated description"
        }

        response = client.patch(
            f"/api/tasks/update/{task.id}/",
            data
        )

        assert response.status_code == 200

        task.refresh_from_db()

        assert task.title == "Updated title"
        assert task.description == "Updated description"

    def test_assignee_cannot_update_task_details(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        task = Task.objects.create(
            title="Original title",
            description="Original description",
            created_by=creator,
            assigned_to=assignee,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=assignee)

        data = {
            "title": "Hacked title",
            "description": "Hacked description"
        }

        response = client.patch(
            f"/api/tasks/update/{task.id}/",
            data
        )

        assert response.status_code == 403

        task.refresh_from_db()

        assert task.title == "Original title"
        assert task.description == "Original description"

    def test_assignee_cannot_delete_task(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        task = Task.objects.create(
            title="Important task",
            created_by=creator,
            assigned_to=assignee,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=assignee)

        response = client.delete(
            f"/api/tasks/delete/{task.id}/"
        )

        assert response.status_code == 403
        assert Task.objects.count() == 1

    def test_creator_can_delete_task(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        task = Task.objects.create(
            title="Task to delete",
            created_by=creator,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.delete(
            f"/api/tasks/delete/{task.id}/"
        )

        assert response.status_code == 204
        assert Task.objects.count() == 0

    def test_unauthenticated_user_cannot_retrieve_task(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        task = Task.objects.create(
            title="Private task",
            created_by=creator,
            due_date=date.today()
        )

        client = APIClient()

        response = client.get(
            f"/api/tasks/list/{task.id}/"
        )

        assert response.status_code == 401

    def test_task_not_found(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.get(
            "/api/tasks/list/9999/"
        )

        assert response.status_code == 404

    def test_creator_cannot_update_status_through_details(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        task = Task.objects.create(
            title="Task",
            created_by=creator,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.patch(
            f"/api/tasks/update/{task.id}/",
            {"status": "completed"}
        )

        assert response.status_code == 400

        task.refresh_from_db()

        assert task.status == "todo"

    def test_past_due_date_is_rejected(self):
        user = User.objects.create_user(
            username="creator",
            password="password123"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/tasks/create/",
            {
                "title": "Late task",
                "description": "This should fail",
                "due_date": "2020-01-01"
            }
        )

        assert response.status_code == 400
        assert Task.objects.count() == 0

    def test_invalid_status_is_rejected(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        task = Task.objects.create(
            title="Task",
            created_by=creator,
            assigned_to=assignee,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=assignee)

        response = client.patch(
            f"/api/tasks/update-status/{task.id}/",
            {"status": "banana"}
        )

        assert response.status_code == 400

        task.refresh_from_db()

        assert task.status == "todo"

    def test_creator_can_assign_task(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        task = Task.objects.create(
            title="Task",
            created_by=creator,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.patch(
            f"/api/tasks/update/{task.id}/",
            {"assigned_to": assignee.id}
        )

        assert response.status_code == 200

        task.refresh_from_db()

        assert task.assigned_to == assignee

    
    def test_assignee_cannot_reassign_task(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        another_user = User.objects.create_user(
            username="another",
            password="password123"
        )

        task = Task.objects.create(
            title="Task",
            created_by=creator,
            assigned_to=assignee,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=assignee)

        response = client.patch(
            f"/api/tasks/update/{task.id}/",
            {"assigned_to": another_user.id}
        )

        assert response.status_code == 403

        task.refresh_from_db()

        assert task.assigned_to == assignee

    def test_task_filters(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        Task.objects.create(
            title="Todo task",
            created_by=creator,
            assigned_to=assignee,
            status="todo",
            due_date=date.today()
        )

        Task.objects.create(
            title="Completed task",
            created_by=creator,
            assigned_to=assignee,
            status="completed",
            due_date=date.today()
        )

        Task.objects.create(
            title="In progress task",
            created_by=creator,
            status="in_progress",
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.get(
            "/api/tasks/list/?status=completed"
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Completed task"

    def test_my_task_filters(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        assignee = User.objects.create_user(
            username="assignee",
            password="password123"
        )

        Task.objects.create(
            title="Created by me",
            created_by=creator,
            due_date=date.today()
        )

        Task.objects.create(
            title="Assigned to me",
            created_by=assignee,
            assigned_to=creator,
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.get(
            "/api/tasks/list/?created_by_me=true"
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Created by me"

        response = client.get(
            "/api/tasks/list/?assigned_to_me=true"
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Assigned to me"

    def test_overdue_and_completed_filters(self):
        creator = User.objects.create_user(
            username="creator",
            password="password123"
        )

        Task.objects.create(
            title="Overdue task",
            created_by=creator,
            status="todo",
            due_date=date.today().replace(day=date.today().day - 1)
        )

        Task.objects.create(
            title="Completed task",
            created_by=creator,
            status="completed",
            due_date=date.today()
        )

        client = APIClient()
        client.force_authenticate(user=creator)

        response = client.get(
            "/api/tasks/list/?over_due=true"
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Overdue task"

        response = client.get(
            "/api/tasks/list/?completed=true"
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Completed task"

    def test_new_task_starts_as_todo(self):
        user = User.objects.create_user(
            username="creator",
            password="password123"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            "/api/tasks/create/",
            {
                "title": "New task",
                "description": "Should start as todo",
                "due_date": str(date.today())
            }
        )

        assert response.status_code == 201

        task = Task.objects.get()

        assert task.status == "todo"