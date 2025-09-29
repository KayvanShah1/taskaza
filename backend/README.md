# 📝 Taskaza – Task Management API

![🚀 Deploy & Test](https://github.com/kayvanshah1/taskaza/actions/workflows/deploy.yml/badge.svg)
![🌀 Keep Taskaza Alive](https://github.com/kayvanshah1/taskaza/actions/workflows/ping-taskaza.yml/badge.svg)

Taskaza is a secure, async API built with FastAPI. It supports user sign-up/login, JWT authentication, API key security, and CRUD operations for tasks.

## 📦 Features

* User registration (`/signup`), profile management (`/users/me`), and login (`/token`, OAuth2 password flow)
* JWT authentication + secure password hashing
* API key header (`X-API-Key: 123456`) on protected routes
* Hierarchical tasks with nested subtasks, priorities, categories, tags, and computed progress
* Rich task querying (status filters, search, pagination, sorting, include/exclude subtasks) plus bulk create/status updates
* Async SQLAlchemy + SQLite (extensible via `TSKZ_DATABASE_URL`), Pydantic v2 validation
* Thorough async tests (unit + integration/auth flows)

[📊 View architecture diagram](docs/ARCHITECTURE.md)

## 🚀 Live Deployment

* 🌐 API: **[https://taskaza.onrender.com](https://taskaza.onrender.com)**
* 📚 Swagger: **[https://taskaza.onrender.com/docs](https://taskaza.onrender.com/docs)**

## 🔐 Authentication (Required for `/tasks/*`)

Send **both** headers on protected routes:

```
Authorization: Bearer <access_token>
X-API-Key: 123456
```

## 📚 API Endpoints

### Auth

| Method | Endpoint    | Description                        |
| ------ | ----------- | ---------------------------------- |
| POST   | `/signup`   | Register a new user                |
| POST   | `/token`    | Exchange username/password for JWT |

### Users (Protected)

| Method | Endpoint          | Description                          |
| ------ | ----------------- | ------------------------------------ |
| GET    | `/users/me`       | Get the authenticated user's profile |
| PUT    | `/users/me`       | Replace the authenticated user's profile |
| PATCH  | `/users/me`       | Partially update your profile        |
| DELETE | `/users/{user_id}` | Delete your own account              |

### Tasks (Protected)

| Method | Endpoint             | Description                                       |
| ------ | -------------------- | ------------------------------------------------- |
| POST   | `/tasks`             | Create a task, optionally with nested subtasks    |
| GET    | `/tasks`             | List tasks with filtering, search, and pagination |
| GET    | `/tasks/{task_id}`   | Retrieve a task (optionally include the subtree)  |
| PUT    | `/tasks/{task_id}`   | Update task fields (partial)                      |
| PATCH  | `/tasks/{task_id}`   | Update only the task status                       |
| DELETE | `/tasks/{task_id}`   | Delete a task                                     |
| POST   | `/tasks/bulk`        | Bulk create tasks and/or change statuses          |

**Extras**

- All `/tasks/*` and `/users/*` endpoints require both `Authorization: Bearer <token>` and `X-API-Key: 123456`.
- `GET /tasks` supports `status`, `q`, `page`, `limit`, `sort`, `include_tree`, and `roots_only` query params.
- `POST /tasks` accepts the `create_subtree` query flag (defaults to `true`) to cascade nested subtasks when provided.

---

## 🛠 Setup with `uv`

> If you don’t have uv:
> **macOS/Linux:**
>
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```
>
> **Windows:**
>
> ```powershell
> winget install --id=astral-sh.uv  -e
> ```

### 1) Clone

```bash
git clone https://github.com/KayvanShah1/taskaza.git
cd taskaza/backend
```

### 2) Install dependencies

```bash
uv sync
```

> 💡 This will automatically create a `.venv/` and install everything from `pyproject.toml` (or lockfile).

### 3) Environment variables

Create a `.env` file:

```ini
TSKZ_JWT_SECRET_KEY=your_generated_jwt_secret_key
TSKZ_HTTP_API_KEY=123456
```

Generate a secure JWT secret key:

```bash
openssl rand -base64 32
```

### 4) Run locally

**Development (auto-reload; tests excluded by default):**

```bash
uv run fastapi dev app/main.py
```

FastAPI already excludes the `tests/` directory from reloads via `pyproject.toml`. To be explicit or customise the ignore pattern:

```bash
# macOS/Linux shells
uv run fastapi dev app/main.py --reload-exclude 'tests/*'

# Windows PowerShell
uv run fastapi dev app/main.py --reload-exclude "tests/*"
```

**Production:**

```bash
uv run fastapi run app/main.py
```

### 5) Docker (optional)

```bash
docker compose up --build
```

App: [http://localhost:8000/](http://localhost:8000/)

Local SQLite data lives in `data/taskaza.db`. Delete the file to reset your environment or set `TSKZ_DATABASE_URL` to point at another database.

---

## 🔁 Export pip-style requirements (for CI/Render)

```bash
# main (no dev)
uv export --format=requirements-txt --no-hashes --no-header --no-annotate --no-dev --output-file requirements.txt

# dev (includes dev dependencies)
uv export --format=requirements-txt --no-hashes --no-header --no-annotate --only-dev --output-file requirements-dev.txt
```

---

## 🧪 Tests

```bash
uv run pytest -v
```

Covers unit tests, full-flow integration, and auth failures.


## 🧰 Postman

Open Postman → **Import** → select [`docs/postman_collection.json`](docs/postman_collection.json).
All requests are preconfigured; just paste your JWT into the **Authorization** header and keep `X-API-Key: 123456`.


## 🖥️ `curl` Quickstart

Set a helper:

```bash
BASE_URL="https://taskaza.onrender.com"   # or http://localhost:8000
```

### Register

```bash
curl -X POST "$BASE_URL/signup" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"strongpassword"}'
```

### Login (get JWT)

```bash
TOKEN=$(curl -s -X POST "$BASE_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=strongpassword" | jq -r .access_token)
```

### Create task

```bash
curl -X POST "$BASE_URL/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-API-Key: 123456" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Task","description":"created via curl","status":"pending"}'
```

### List tasks

```bash
curl -X GET "$BASE_URL/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-API-Key: 123456"
```

### Update status

```bash
curl -X PATCH "$BASE_URL/tasks/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-API-Key: 123456" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'
```

### Update entire task

```bash
curl -X PUT "$BASE_URL/tasks/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-API-Key: 123456" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated via curl","description":"Updated from terminal","status":"completed"}'
```

### Delete

```bash
curl -X DELETE "$BASE_URL/tasks/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-API-Key: 123456"
```
