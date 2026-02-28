from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
import os
import hashlib

from app.database import get_db
from app.models.file import File as FileModel
from app.models.chunk import Chunk
from app.services.storage import save_file_in_chunks

router = APIRouter()

STORAGE_PATH = "storage"


# --------------------------------------------------
# Upload Endpoint
# --------------------------------------------------
@router.post("/upload")
async def upload_file(
    owner: str,
    uploaded_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    file_id = uuid4()

    total_size, total_chunks, chunk_metadata = save_file_in_chunks(
        uploaded_file.file,
        file_id
    )

    new_file = FileModel(
        id=file_id,
        filename=uploaded_file.filename,
        owner=owner,
        total_size=total_size,
        total_chunks=total_chunks,
        status="HEALTHY"
    )

    db.add(new_file)
    db.flush()

    for chunk in chunk_metadata:
        for path in chunk["chunk_paths"]:
            new_chunk = Chunk(
                file_id=file_id,
                chunk_index=chunk["chunk_index"],
                chunk_hash=chunk["chunk_hash"],
                chunk_path=path
            )
            db.add(new_chunk)

    db.commit()
    db.refresh(new_file)

    return {
        "file_id": str(file_id),
        "filename": uploaded_file.filename,
        "size": total_size,
        "chunks": total_chunks,
        "status": new_file.status
    }


# --------------------------------------------------
# List All Files
# --------------------------------------------------
@router.get("/files")
def list_files(db: Session = Depends(get_db)):

    files = db.query(FileModel).all()

    return [
        {
            "file_id": str(file.id),
            "filename": file.filename,
            "owner": file.owner,
            "size": file.total_size,
            "chunks": file.total_chunks,
            "status": file.status,
            "created_at": file.created_at
        }
        for file in files
    ]


# --------------------------------------------------
# Get Single File Metadata
# --------------------------------------------------
@router.get("/files/{file_id}")
def get_file_metadata(file_id: str, db: Session = Depends(get_db)):

    try:
        file_uuid = UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file_id format")

    file = db.query(FileModel).filter(FileModel.id == file_uuid).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    chunks = (
        db.query(Chunk)
        .filter(Chunk.file_id == file_uuid)
        .order_by(Chunk.chunk_index)
        .all()
    )

    return {
        "file_id": str(file.id),
        "filename": file.filename,
        "owner": file.owner,
        "size": file.total_size,
        "status": file.status,
        "chunks": [
            {
                "chunk_index": c.chunk_index,
                "chunk_hash": c.chunk_hash,
                "chunk_path": c.chunk_path
            }
            for c in chunks
        ]
    }


# --------------------------------------------------
# Download Endpoint (Integrity + Self-Healing + Status Tracking)
# --------------------------------------------------
@router.get("/download/{file_id}")
def download_file(file_id: str, db: Session = Depends(get_db)):

    try:
        file_uuid = UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file_id format")

    file_entry = db.query(FileModel).filter(FileModel.id == file_uuid).first()

    if not file_entry:
        raise HTTPException(status_code=404, detail="File not found")

    chunks = (
        db.query(Chunk)
        .filter(Chunk.file_id == file_uuid)
        .order_by(Chunk.chunk_index)
        .all()
    )

    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found")

    def file_generator():

        from collections import defaultdict

        chunk_groups = defaultdict(list)
        repaired_any = False

        # Group replicas by chunk index
        for c in chunks:
            chunk_groups[c.chunk_index].append(c)

        # Process each chunk
        for chunk_index in sorted(chunk_groups.keys()):

            replicas = chunk_groups[chunk_index]
            valid_data = None
            valid_hash = None

            # ---------- First pass: find healthy replica ----------
            for replica in replicas:

                if not os.path.exists(replica.chunk_path):
                    continue

                with open(replica.chunk_path, "rb") as f:
                    data = f.read()

                computed_hash = hashlib.sha256(data).hexdigest()

                if computed_hash == replica.chunk_hash:
                    valid_data = data
                    valid_hash = computed_hash
                    break

            # If no valid replica found → file is DEAD
            if not valid_data:
                file_entry.status = "DEAD"
                db.commit()

                raise HTTPException(
                    status_code=500,
                    detail=f"All replicas corrupted for chunk {chunk_index}"
                )

            # ---------- Second pass: repair corrupted replicas ----------
            for replica in replicas:

                if not os.path.exists(replica.chunk_path):
                    continue

                with open(replica.chunk_path, "rb") as f:
                    data = f.read()

                computed_hash = hashlib.sha256(data).hexdigest()

                if computed_hash != valid_hash:
                    with open(replica.chunk_path, "wb") as f:
                        f.write(valid_data)

                    repaired_any = True

            yield valid_data

        # After processing all chunks → update health state
        if repaired_any:
            file_entry.status = "DEGRADED"
        else:
            file_entry.status = "HEALTHY"

        db.commit()

    return StreamingResponse(
        file_generator(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file_entry.filename}"
        },
    )

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models.file import File as FileModel
from app.models.chunk import Chunk


@router.delete("/files/{file_id}")
def delete_file(file_id: str, db: Session = Depends(get_db)):

    file = db.query(FileModel).filter(FileModel.id == file_id).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete chunks from disk
    chunks = db.query(Chunk).filter(Chunk.file_id == file_id).all()

    for chunk in chunks:
        if os.path.exists(chunk.chunk_path):
            os.remove(chunk.chunk_path)

    # Delete from database
    db.query(Chunk).filter(Chunk.file_id == file_id).delete()
    db.delete(file)

    db.commit()

    return {"message": "File deleted successfully"}

