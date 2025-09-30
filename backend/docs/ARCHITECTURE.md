## 🧱 Architecture

The **Taskaza** API is a secure, containerized task management system built with FastAPI, designed around clean separation of concerns, robust authentication, and cloud-native deployment.

```mermaid
---
config:
  theme: neo-dark
---

graph TD
  A[Client: Postman / Browser] --> B[FastAPI App]

  subgraph FastAPI Layer
    B --> C1[Auth Router]
    B --> C2[Tasks Router]
    B --> C3[Users Router]
    C1 --> D1[JWT Auth]
    C1 --> D2[API Key Verification]
    C2 --> D3[CRUD Logic]
    C3 --> D4[Signup & User Management]
  end

  D1 --> E[Dependency Injection]
  D2 --> E
  D3 --> E
  D4 --> E

  E --> F[Async SQLAlchemy Models]
  F --> G[SQLite DB data/taskaza.db]

  B --> H[.env Config Loader]

  subgraph CI/CD Pipeline
    direction TB

    K[GitHub Actions]
    K --> L1

    subgraph GitHub CI Jobs
      L1[Build + Test] --> L2[Build Docker Image]
      L2 --> L3[Push to Docker Hub]
      L3 --> L4[Deploy to Render]
    end
  end

  L4 --> M[Render Cloud Runtime]
  M -->|Runs Container| J[Docker Container]
  J --> I[Uvicorn Server]
  M -->|Reads/Writes| G

```

### 🔐 Security

* **OAuth2 + JWT** authentication with secure password hashing
* **API Key** validation for all protected routes
* `.env`-based secret injection (or Render env dashboard)

### Data Model

The ER diagram below captures the core tables and relationships for user-owned tasks, including self-referential parent-child links.

```mermaid
---
config:
  theme: mc
  layout: elk
---
erDiagram
    USERS ||--o{ TASKS : "user_id (ON DELETE CASCADE)"
    TASKS ||--o{ TASKS : "parent_id (ON DELETE SET NULL)"

    USERS {
      INT id PK
      TEXT username "UNIQUE NOT NULL"
      TEXT email "UNIQUE"
      TEXT display_name
      TEXT password_hash "NOT NULL"
      BOOLEAN email_verified "DEFAULT false"
      TIMESTAMP created_at
      TIMESTAMP updated_at
    }

    TASKS {
      INT id PK
      INT user_id "FK -> USERS.id"
      INT parent_id "FK -> TASKS.id"
      TEXT title "NOT NULL"
      TEXT description
      TEXT status "ENUM(todo,in_progress,completed,cancelled) DEFAULT 'todo'"
      TEXT priority "ENUM(low,medium,high,urgent) DEFAULT 'medium'"
      TEXT category "ENUM(work,personal,shopping,health,learning,finance,family,travel) DEFAULT 'personal'"
      JSON tags
      DATE due_date
      NUMERIC estimated_hours
      NUMERIC actual_hours
      TEXT notes
      TIMESTAMP completed_date
      TIMESTAMP created_at
      TIMESTAMP updated_at
      INT progress "virtual/computed"
    }
```

### State Diagram
- For Task.status transitions & rules
- When: preventing invalid updates in UI/backend.
```mermaid
stateDiagram-v2
  [*] --> todo
  todo --> in_progress
  in_progress --> completed
  in_progress --> cancelled
  todo --> cancelled
  completed --> [*]
  cancelled --> [*]
```


### ⚙️ Components

| Layer           | Description                                                       |
| --------------- | ----------------------------------------------------------------- |
| **FastAPI**     | Async REST API framework with dependency injection                |
| **Auth**        | OAuth2 Password flow (JWT) + API Key (`X-API-Key`)                |
| **Database**    | SQLite with async SQLAlchemy models                               |
| **Pydantic v2** | Input/output schema validation with examples                      |
| **Docker**      | Containerized build for reproducible deployment                   |
| **CI/CD**       | GitHub Actions: test → build Docker → deploy to Render            |
| **Render**      | Cloud platform running Docker-based deployment with auto-redeploy |