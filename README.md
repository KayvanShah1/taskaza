# 📝 Taskaza – FastAPI Task Management API

![🚀 Deploy & Test](https://github.com/kayvanshah1/taskaza/actions/workflows/deploy.yml/badge.svg)
![🌀 Keep Taskaza Alive](https://github.com/kayvanshah1/taskaza/actions/workflows/ping-taskaza.yml/badge.svg)

Taskaza is a secure, async, full-stack API built with FastAPI. It supports user sign-up/login, JWT authentication, API key security, and CRUD operations for tasks.

## 📦 Features
- ✅ User Registration (`/signup`)
- ✅ OAuth2 Password Flow Login (`/token`)
- ✅ JWT Authentication & Secure Password Hashing
- ✅ API Key Header Required (`X-API-Key: 123456`)
- ✅ Task CRUD (Create, Read, Update, Delete)
- ✅ Protected Endpoints (JWT + API key required)
- ✅ Async SQLAlchemy + SQLite
- ✅ Pydantic validation, proper error handling

[📊 View architecture diagram](docs/ARCHITECTURE.md)

## 🚀 Live Deployment

🌐 **Live API URL:** [taskaza.onrender.com](https://taskaza.onrender.com)

📚 **Swagger UI:** [taskaza.onrender.com/docs](https://taskaza.onrender.com/docs)

## 🔐 Authentication

All `/tasks/*` routes are protected using:

1. ✅ **JWT Bearer Token**
2. ✅ **`X-API-Key: 123456`**

You **must** send both headers:

```xml
Authorization: Bearer <access_token>
X-API-Key: 123456
````


## 📚 API Endpoints

### 🧑 User Routes

| Method | Endpoint     | Description              |
|--------|--------------|--------------------------|
| POST   | `/signup`    | Register a new user      |
| POST   | `/token`     | Login and get JWT token  |

### 📋 Task Routes (Protected)

| Method | Endpoint        | Description                  |
|--------|------------------|------------------------------|
| POST   | `/tasks/`        | Create a task                |
| GET    | `/tasks/`        | List all tasks (own user)    |
| GET    | `/tasks/{id}`    | Get a specific task          |
| PATCH  | `/tasks/{id}`    | Update task status only      |
| PUT    | `/tasks/{id}`    | Update full task             |
| DELETE | `/tasks/{id}`    | Delete a task                |


## 🛠 Project Setup

### 1️⃣ Clone the repo

```bash
git clone https://github.com/KayvanShah1/taskaza.git
cd taskaza
````

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

### 3️⃣ Create a `.env` file

```ini
# .env

# Secret key used to sign JWT tokens (generate one below)
TSKZ_JWT_SECRET_KEY=your_generated_jwt_secret_key

# API Key required for protected endpoints
TSKZ_HTTP_API_KEY=123456
```

To generate a secure JWT secret key, run:

```bash
openssl rand -base64 32
```

### 4️⃣ Run the app locally without docker
**Development server**
```bash
fastapi dev app/main.py
```

**Production server**
```bash
fastapi run app/main.py
```

#### 🐳 Run using Docker Compose
```bash
docker-compose up --build
```
> Make sure your .env file is present in the root directory.
App will be available at: http://localhost:8000/

## 🧪 Run Tests

```bash
pytest -v
```

Includes:

* ✅ Unit tests for each endpoint
* 🔁 Full-flow integration tests
* 🔐 Auth failure scenarios


## 🔐 Example Usage

> For all `/tasks/*` routes, include both:
>
> * `Authorization: Bearer <your_token>`
> * `X-API-Key: 123456`

### 🧑 User Endpoints

#### ✅ Register a user

```http
POST /signup
Content-Type: application/json

{
  "username": "testuser",
  "password": "strongpassword"
}
```

#### ✅ Login and receive JWT token

```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=testuser&password=strongpassword
```

*Response:*

```json
{
  "access_token": "your.jwt.token",
  "token_type": "bearer"
}
```

### 📋 Task Endpoints

#### ✅ Create Task

```http
POST /tasks/
Headers:
  Authorization: Bearer <your_token>
  X-API-Key: 123456
Content-Type: application/json

{
  "title": "New Task",
  "description": "Finish the assignment",
  "status": "pending"
}
```

#### 📥 Get All Tasks

```http
GET /tasks/
Headers:
  Authorization: Bearer <your_token>
  X-API-Key: 123456
```

#### 🔍 Get Task by ID

```http
GET /tasks/1
Headers:
  Authorization: Bearer <your_token>
  X-API-Key: 123456
```

#### 🔄 Update Task Status

```http
PATCH /tasks/1
Headers:
  Authorization: Bearer <your_token>
  X-API-Key: 123456
Content-Type: application/json

{
  "status": "completed"
}
```

#### 📝 Update Entire Task

```http
PUT /tasks/1
Headers:
  Authorization: Bearer <your_token>
  X-API-Key: 123456
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated desc",
  "status": "completed"
}
```

#### ❌ Delete Task

```http
DELETE /tasks/1
Headers:
  Authorization: Bearer <your_token>
  X-API-Key: 123456
```

*Response:*

```
204 No Content
```

## Using Postman
To use the API in **Postman**, open Postman, click **Import**, then select the [`docs/postman_collection.json`](docs/postman_collection.json) file to load all predefined requests.

## Using `curl` to Interact with Taskaza
You can test the live API from your terminal using simple `curl` commands.
> Same can be used to test the local development server.

### Register a new user

```bash
curl -X POST https://taskaza.onrender.com/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "strongpassword"}'
```

### Login and get JWT token

```bash
curl -X POST https://taskaza.onrender.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=strongpassword"
```

> Save the `access_token` from the response for next steps.

### Create a new task

```bash
curl -X POST https://taskaza.onrender.com/tasks/ \
  -H "Authorization: Bearer <your_token>" \
  -H "X-API-Key: 123456" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Task", "description": "curl-based creation", "status": "pending"}'
```

### Get all tasks

```bash
curl -X GET https://taskaza.onrender.com/tasks/ \
  -H "Authorization: Bearer <your_token>" \
  -H "X-API-Key: 123456"
```

### Update task status

```bash
curl -X PATCH https://taskaza.onrender.com/tasks/1 \
  -H "Authorization: Bearer <your_token>" \
  -H "X-API-Key: 123456" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Update an entire task

```bash
curl -X PUT https://taskaza.onrender.com/tasks/1 \
  -H "Authorization: Bearer <your_token>" \
  -H "X-API-Key: 123456" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated via curl",
    "description": "Updated description from terminal",
    "status": "completed"
  }
  ```

### Delete a task

```bash
curl -X DELETE https://taskaza.onrender.com/tasks/1 \
  -H "Authorization: Bearer <your_token>" \
  -H "X-API-Key: 123456"
```

> Replace `<your_token>` with your actual JWT access token.


## 📁 Tech Stack

* FastAPI (async)
* SQLite (local/test db)
* SQLAlchemy 2.0 (async ORM)
* Pydantic v2
* JWT (OAuth2 password flow)
* Passlib (bcrypt)
* Pytest + httpx


## 📜 License
MIT © 2025 Kayvan Shah. All rights reserved.

This repository is licensed under the `MIT` License. See the [LICENSE](LICENSE) file for details.

#### Disclaimer

<sub>
The content and code provided in this repository are for educational and demonstrative purposes only. The project may contain experimental features, and the code might not be optimized for production environments. The authors and contributors are not liable for any misuse, damages, or risks associated with the use of this code. Users are advised to review, test, and modify the code to suit their specific use cases and requirements. By using any part of this project, you agree to these terms.
</sub>
