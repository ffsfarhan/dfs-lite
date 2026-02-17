from app.routes.cluster import router as cluster_router
from app.services.node_manager import initialize_nodes
from fastapi import FastAPI
from app.database import engine, Base
from app.models.file import File
from app.models.chunk import Chunk
from app.models.node import Node   # <-- THIS MUST EXIST
from app.routes.files import router as file_router
from app.routes.nodes import router as node_router
import threading
from app.services.repair import repair_daemon

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(file_router)
app.include_router(node_router)
app.include_router(cluster_router)

@app.get("/")
def root():
    return {"message": "DFS Lite Running"}

@app.on_event("startup")
def start_background_services():

    initialize_nodes()

    thread = threading.Thread(target=repair_daemon, daemon=True)
    thread.start()

