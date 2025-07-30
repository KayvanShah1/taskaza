from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import tasks, users
from app.core import metadata
from app.core.config import settings

app = FastAPI(
    title="Taskaza API",
    version="1.0.0",
    description=metadata.description,
    summary=metadata.summary,
    terms_of_service="https://github.com/kayvanshah1/taskaza/blob/main/LICENSE",
    contact=metadata.contact,
    license_info=metadata.license_info,
    openapi_tags=metadata.tags_metadata,
)

# Handle CORS protection
origins = settings.BACKEND_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, tags=["Users"])
app.include_router(tasks.router, tags=["Tasks"])
