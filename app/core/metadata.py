description = """
Taskaza is a focused and secure task management API built with FastAPI, JWT authentication, and API key protection.

Features:
- User signup/login with hashed passwords
- OAuth2 password flow with JWT token issuance
- Task creation, listing, and updates
- SQLite-backed persistence via SQLAlchemy
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
