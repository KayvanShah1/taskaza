## 🧱 Architecture

The **Taskaza** API is a secure, containerized task management system built with FastAPI, designed around clean separation of concerns, robust authentication, and cloud-native deployment.

```mermaid
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

  E --> F[Async SQLAlchemy Models]
  F --> G[SQLite DB data/taskaza.db]

  B --> H[.env Config Loader]
  B --> I[Uvicorn Server]

  %% runtime wrapper for FastAPI app
  I --> J[Docker Container]

  subgraph CI/CD Pipeline
    K[GitHub Actions]

    subgraph GitHub CI Jobs
      K --> L1[Build + Test]
      L1 --> L2[Build Docker Image]
      L2 --> J
      L2 --> L3[Push to Docker Hub]
      L3 --> L4[Deploy to Render]
    end
  end

  L4 --> M[Render Cloud Runtime]
  M -->|Runs Container| J
  M -->|Reads/Writes| G
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

---

### 🔐 Security

* **OAuth2 + JWT** authentication with secure password hashing
* **API Key** validation for all protected routes
* `.env`-based secret injection (or Render env dashboard)
