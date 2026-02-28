from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading

from app.database import engine, Base
from app.models.file import File
from app.models.chunk import Chunk
from app.models.node import Node

from app.routes.files import router as file_router
from app.routes.nodes import router as node_router
from app.routes.cluster import router as cluster_router

from app.services.repair import repair_daemon
from app.services.node_manager import initialize_nodes


app = FastAPI(title="DFS Lite")


# -----------------------------
# Enable CORS for Frontend
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Create Tables
# -----------------------------
Base.metadata.create_all(bind=engine)


# -----------------------------
# Register Routers
# -----------------------------
app.include_router(file_router)
app.include_router(node_router)
app.include_router(cluster_router)


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "DFS Lite Running"}


# -----------------------------
# Startup Services
# -----------------------------
@app.on_event("startup")
def start_background_services():

    # Initialize storage nodes in DB
    initialize_nodes()

    # Start background repair daemon
    thread = threading.Thread(target=repair_daemon, daemon=True)
    thread.start()

