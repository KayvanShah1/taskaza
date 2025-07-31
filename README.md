# 📝 Taskaza – FastAPI Task Management API

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

## 🚀 Live Deployment

🌐 **Live API URL:** [taskaza.onrender.com](https://taskaza.onrender.com)

📚 **Swagger UI:** [taskaza.onrender.com/docs](https://taskaza.onrender.com/docs)

## 🔐 Authentication

All `/tasks/*` routes are protected using:

1. ✅ **JWT Bearer Token**
2. ✅ **`X-API-Key: 123456`**

You **must** send both headers:

```html
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

### 3️⃣ Run the app locally
**Development server**
```bash
fastapi dev app/main.py
```

**Production server**
```bash
fastapi run app/main.py
```

## 🧪 Run Tests

```bash
pytest -v
```

Includes:

* ✅ Unit tests for each endpoint
* 🔁 Full-flow integration tests
* 🔐 Auth failure scenarios


## 🔐 Example Usage

### ✅ Register a user

```http
POST /signup
{
  "username": "testuser",
  "password": "strongpassword"
}
```

### ✅ Login

```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=testuser&password=strongpassword
```

### ✅ Create Task

```http
POST /tasks/
Headers:
  Authorization: Bearer <your_token>
  X-API-Key: 123456

{
  "title": "Test Task",
  "description": "This is a test",
  "status": "pending"
}
```

#### LICENSE
This repository is licensed under the `MIT` License. See the [LICENSE](LICENSE) file for details.

#### Disclaimer

<sub>
The content and code provided in this repository are for educational and demonstrative purposes only. The project may contain experimental features, and the code might not be optimized for production environments. The authors and contributors are not liable for any misuse, damages, or risks associated with the use of this code. Users are advised to review, test, and modify the code to suit their specific use cases and requirements. By using any part of this project, you agree to these terms.
</sub>
