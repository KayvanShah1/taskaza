description = """Taskaza is a lightweight, production-ready task management API built with **FastAPI**.
It provides a secure foundation for user and task management with modern authentication mechanisms.

### Key Features
- 🔑 **Authentication**: JWT (OAuth2 password flow) + API Key security
- 👤 **User Accounts**: Sign up and login with secure password hashing
- ✅ **Task Management**: Create, read, update, and delete tasks
- 📦 **Bulk Operations**: Efficient handling of multiple tasks
- 🛡️ **Database Support**: Async SQLite for local dev, PostgreSQL for production
- 📖 **OpenAPI Docs**: Interactive Swagger UI and ReDoc support
"""

summary = "Taskaza – Secure, Async Task Management API"

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
