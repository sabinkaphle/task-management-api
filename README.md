# Task Management API

A RESTful Task Management API built with **Django REST Framework**.
The API supports user authentication with JWT, task creation and assignment, status management, permissions, filtering, validation, automated tests, API documentation, and PostgreSQL deployment.

## Live API

**Swagger UI:**
https://task-management-api-mxbj.onrender.com/api/schema/swagger-ui/

**OpenAPI Schema:**
https://task-management-api-mxbj.onrender.com/api/schema/

> The API is deployed on Render using the free tier and uses PostgreSQL hosted on Neon.

---

## Features

* User registration and authentication
* JWT access and refresh tokens
* Create, read, update, and delete tasks
* Assign tasks to other users
* Optional task assignment
* Task status management
* Creator and assignee-based permissions
* Task filtering
* Input validation
* PostgreSQL database support
* SQLite database for local development
* Automated API tests
* OpenAPI schema generation
* Swagger UI documentation
* Gunicorn production server
* Environment-based configuration
* Deployment-ready configuration

---

## Tech Stack

| Technology            | Purpose                               |
| --------------------- | ------------------------------------- |
| Python                | Programming language                  |
| Django                | Web framework                         |
| Django REST Framework | REST API development                  |
| Simple JWT            | JWT authentication                    |
| PostgreSQL            | Production database                   |
| SQLite                | Local development database            |
| Gunicorn              | Production WSGI server                |
| drf-spectacular       | OpenAPI/Swagger documentation         |
| dj-database-url       | Database URL configuration            |
| python-dotenv         | Environment variable management       |
| uv                    | Python package and project management |
| Render                | API hosting                           |
| Neon                  | PostgreSQL hosting                    |

---

## Project Structure

```text
Task Manager API/
│
├── apps/
│   ├── accounts/
│   │   └── api/
│   │       └── urls.py
│   │
│   └── tasks/
│       ├── api/
│       │   ├── serializers.py
│       │   ├── urls.py
│       │   └── views.py
│       │
│       ├── migrations/
│       ├── models.py
│       ├── permissions.py
│       └── tests/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── manage.py
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

---

# Authentication

The API uses **JWT authentication**.

Users can register and then log in to receive:

* Access token
* Refresh token

### Register

```http
POST /api/auth/register/
```

Example:

```json
{
  "username": "testing",
  "password": "testing123"
}
```

### Login

```http
POST /api/auth/login/
```

Example:

```json
{
  "username": "testing",
  "password": "testing123"
}
```

Example response:

```json
{
  "refresh_token": "YOUR_REFRESH_TOKEN",
  "access_token": "YOUR_ACCESS_TOKEN"
}
```

For authenticated requests, include the access token:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Current User

```http
GET /api/auth/me/
```

---

# Task API

## Create Task

```http
POST /api/tasks/create/
```

Example:

```json
{
  "title": "Complete API documentation",
  "description": "Write the README and API documentation.",
  "assigned_to": 2,
  "due_date": "2026-09-30"
}
```

### Unassigned Task

A task does not have to be assigned immediately.

For example:

```json
{
  "title": "Complete API documentation",
  "description": "Write the README and API documentation.",
  "assigned_to": null,
  "due_date": "2026-09-30"
}
```

The `assigned_to` field can therefore remain `null` when nobody is currently assigned.

---

## List Tasks

```http
GET /api/tasks/list/
```

Returns tasks accessible to the authenticated user.

---

## Retrieve Task

```http
GET /api/tasks/list/<id>/
```

Example:

```http
GET /api/tasks/list/1/
```

A task can be retrieved by its creator or assigned user.

---

## Update Task

```http
PATCH /api/tasks/update/<id>/
```

The task creator can update task details and assignment.

Example:

```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "assigned_to": 2,
  "due_date": "2026-10-01"
}
```

---

## Update Task Status

```http
PATCH /api/tasks/update-status/<id>/
```

Example:

```json
{
  "status": "IN_PROGRESS"
}
```

Available statuses:

```text
TODO
IN_PROGRESS
COMPLETED
```

The assigned user can update the task status.

---

## Delete Task

```http
DELETE /api/tasks/delete/<id>/
```

Only the task creator can delete a task.

---

# Permission Rules

The API uses object-level permissions to control access to tasks.

| Action            | Creator | Assignee | Other authenticated users |
| ----------------- | ------- | -------- | ------------------------- |
| Create task       | Yes     | Yes      | Yes                       |
| View task         | Yes     | Yes      | No                        |
| Edit task details | Yes     | No       | No                        |
| Assign task       | Yes     | No       | No                        |
| Delete task       | Yes     | No       | No                        |
| Update status     | Yes*    | Yes      | No                        |

`*` Status changes are handled through the dedicated status endpoint according to the application's permission rules.

Unauthenticated requests are rejected with:

```http
401 Unauthorized
```

---

# Task Model

A task contains the following information:

| Field         | Description               |
| ------------- | ------------------------- |
| `id`          | Unique task identifier    |
| `title`       | Task title                |
| `description` | Task description          |
| `created_by`  | User who created the task |
| `assigned_to` | User assigned to the task |
| `status`      | Current task status       |
| `due_date`    | Optional task deadline    |
| `created_at`  | Task creation timestamp   |
| `updated_at`  | Last update timestamp     |

### Assignment

Task assignment is optional.

A task can be created without an assignee:

```text
assigned_to = NULL
```

This allows a task to be created first and assigned later when a suitable user becomes available.

---

# Filtering

The task list endpoint supports filtering based on task information.

```http
GET /api/tasks/list/
```

Filtering can be used to retrieve relevant tasks without requesting the entire task collection.

---

# API Documentation

The project uses **drf-spectacular** to generate an OpenAPI 3 schema.

### OpenAPI Schema

```http
GET /api/schema/
```

### Swagger UI

```http
GET /api/schema/swagger-ui/
```

The Swagger interface provides an interactive way to test the API endpoints.

---

# Local Development

## 1. Clone the repository

```bash
git clone https://github.com/sabinkaphle/task-management-api.git
cd task-management-api
```

## 2. Install dependencies

This project uses `uv`.

```bash
uv sync
```

## 3. Create environment variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=
ALLOWED_HOSTS=localhost,127.0.0.1
```

For local development, leaving `DATABASE_URL` empty allows the project to use SQLite.

> Never commit your `.env` file to Git.

## 4. Apply migrations

```bash
python manage.py migrate
```

## 5. Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

Swagger UI:

```text
http://127.0.0.1:8000/api/schema/swagger-ui/
```

---

# Database Configuration

The project uses different databases depending on the environment.

### Local Development

SQLite is used by default:

```text
db.sqlite3
```

### Production

When `DATABASE_URL` is provided, `dj-database-url` configures Django to use PostgreSQL.

This allows the same Django project to work with SQLite locally and PostgreSQL in production without changing the application code.

---

# Deployment

The API is deployed using:

* **Render** — application hosting
* **Neon** — PostgreSQL database

The production server runs Gunicorn.

Render uses:

```bash
python manage.py migrate && gunicorn config.wsgi:application
```

This applies any pending migrations before starting the application server.

---

# Environment Variables

The following environment variables are used in production:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=your-neon-postgresql-connection-string
ALLOWED_HOSTS=your-render-hostname
```

Sensitive values such as `SECRET_KEY` and `DATABASE_URL` should never be committed to GitHub.

---

# Known Issue: Swagger `assigned_to` Defaults to `0`

When testing the task creation endpoint through Swagger UI, the generated request body may show:

```json
{
  "title": "Test task",
  "description": "Testing deployment",
  "assigned_to": 0,
  "due_date": "2026-09-30"
}
```

`0` is not a valid user ID, so sending the request can produce an error indicating that a user with ID `0` does not exist.

### Workaround

Because `assigned_to` is optional, either remove the field from the request or explicitly set it to `null`:

```json
{
  "title": "Test task",
  "description": "Testing deployment",
  "assigned_to": null,
  "due_date": "2026-09-30"
}
```

Alternatively, provide the ID of an existing user:

```json
{
  "title": "Test task",
  "description": "Testing deployment",
  "assigned_to": 2,
  "due_date": "2026-09-30"
}
```

This issue is related to the generated Swagger request example/default rather than PostgreSQL or the deployed server.

---

# Testing

The project includes automated tests covering API behavior, authentication, permissions, validation, task operations, and status updates.

Run the test suite with:

```bash
python manage.py test
```

The project currently has **24 automated tests**.

---

# Security Considerations

* JWT authentication is used for protected API endpoints.
* Passwords are write-only and are never returned in API responses.
* Django's password hashing is used for storing user passwords.
* Secrets are stored through environment variables.
* `.env` and the local SQLite database are excluded from Git.
* Object-level permissions prevent users from accessing tasks they do not own or have not been assigned.
* Production uses PostgreSQL instead of SQLite.

---

# Future Improvements

Possible future improvements include:

* Pagination
* More advanced task filtering
* Search
* Email notifications
* Password reset
* Task priority
* Task categories
* Rate limiting
* Improved production logging
* CI/CD with GitHub Actions
* More comprehensive API test coverage
* Production static-file handling
* Custom API error responses

---

# License

This project is currently intended as a personal learning and portfolio project.
