"""
FastAPI application entrypoint for the AI-First HCP CRM backend.
"""
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# =====================================================================
# PATH FIX: Ensures Python and Uvicorn can resolve the 'app' module
# =====================================================================
CURRENT_DIR = Path(__file__).resolve().parent      # Points to 'app'
PROJECT_ROOT = CURRENT_DIR.parent                  # Points to 'AI-CRM-main'

# Inject project root into Python's search path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Inject into the environment path so Uvicorn child-processes can see it
os.environ["PYTHONPATH"] = str(PROJECT_ROOT)
# =====================================================================

# Now safe to import from the 'app' package package-wide
from app.config import settings
from app.database import Base, engine
from app.routes import interactions, chat

# Import models so they register with Base.metadata before create_all
from app.models import hcp, interaction, followup  # noqa: F401

# Generate your database tables locally
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-First HCP CRM API",
    description="Backend for the HCP Log Interaction module — structured form + conversational AI chat.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interactions.router)
app.include_router(chat.router)


@app.get("/")
def read_root():
    """
    Automatically redirects anyone visiting the base URL directly to the interactive docs.
    """
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    return {"status": "ok", "env": settings.ENV}


if __name__ == "__main__":
    import uvicorn
    # Clean programmatic execution hook
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)




