description = """
## 🚀 How to Use the API

### 1️⃣ Register a New User
Send a `POST` request to `/signup` with:

```json
{
  "username": "your_username",
  "password": "your_password"
}
````

### 2️⃣ Authorize in Swagger UI

This API uses both **JWT** and **API key** authentication.

To authorize via Swagger UI:

* Click the **"Authorize"** button near the top-right corner
* In the **OAuth2 fields**, enter:

  * **Username**: `your_username`
  * **Password**: `your_password`
* In the **API Key field**, enter:

  * **X-API-Key**: `123456`

Once authorized, you’ll be able to call the protected `/tasks/*` endpoints.

## 📦 Task Operations Overview

All `/tasks/*` routes require both a valid JWT token and the `X-API-Key` header.

### ✅ Create a Task

Send a `POST` request to `/tasks/` with:

```json
{
  "title": "My Task",
  "description": "Do something important",
  "status": "pending"
}
```

### 📋 List All Tasks

Send a `GET` request to `/tasks/`
Returns all tasks belonging to the authenticated user.

### 🔁 Update a Task (Full Update)

Send a `PUT` request to `/tasks/{id}` with:

```json
{
  "title": "Updated Task",
  "description": "Updated details",
  "status": "completed"
}
```

### Update Task Status Only

Send a `PATCH` request to `/tasks/{id}` with:

```json
{
  "status": "completed"
}
```

### Delete a Task

Send a `DELETE` request to `/tasks/{id}`
Deletes the specified task if it belongs to the authenticated user.
"""

summary = "A lightweight, secure task management API with JWT + API key auth."

contact = {
    "name": "Kayvan Shah",
    "url": "https://kayvanshah1.github.io",
    "email": "kayvan.taiyo@gmail.com",
}

license_info = {
    "name": "MIT License",
    "url": "https://opensource.org/licenses/MIT",
}

tags_metadata = [
    {"name": "Users", "description": "User registration and login routes"},
    {"name": "Login", "description": "Authentication and token management routes"},
    {"name": "Tasks", "description": "CRUD operations for user tasks"},
]
