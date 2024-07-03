from builtins import Exception
from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware  # Import the CORSMiddleware
from app.database import Database
from app.dependencies import get_settings
from app.routers import api_routes
from app.utils.api_description import getDescription
app = FastAPI(
    root_path="/api",
    title="FastAPi with RAG",
    description=getDescription(),
    version="0.0.1",
    contact={
        "name": "API Support",
        "url": "https://github.com/joec11/is690_midterm",
        "email": "support@example.com",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)
# CORS middleware configuration
# This middleware will enable CORS and allow requests from any origin
# It can be configured to allow specific methods, headers, and origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Update this to match your Next.js app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    Database.initialize(settings.database_url, settings.debug)

app.include_router(api_routes.router)
