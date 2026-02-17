from fastapi import FastAPI
from app.database import engine, Base
from app.models.file import File
from app.routes.files import router as file_router
from app.models.chunk import Chunk

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(file_router)

@app.get("/")
def root():
    return {"message": "DFS Lite Running"}

