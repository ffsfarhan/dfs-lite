import os
import hashlib
import random

from app.database import SessionLocal
from app.models.node import Node
from app.config import settings

CHUNK_SIZE = 1024 * 1024  # 1MB per chunk


def save_file_in_chunks(file_obj, file_id):

    db = SessionLocal()

    # Fetch online nodes dynamically from database
    online_nodes = db.query(Node).filter(Node.is_online == True).all()

    if len(online_nodes) < settings.REPLICATION_FACTOR:
        db.close()
        raise Exception("Not enough online nodes to satisfy replication factor")

    total_size = 0
    chunk_index = 0
    chunk_metadata = []

    while True:
        chunk_data = file_obj.read(CHUNK_SIZE)
        if not chunk_data:
            break

        total_size += len(chunk_data)

        # Calculate SHA-256 hash
        chunk_hash = hashlib.sha256(chunk_data).hexdigest()

        # Select Node OBJECTS (not ids)
        selected_nodes = random.sample(
            online_nodes,
            settings.REPLICATION_FACTOR
        )

        chunk_paths = []

        for node in selected_nodes:

            node_path = node.path  # ✅ use stored DB path

            os.makedirs(node_path, exist_ok=True)

            chunk_filename = f"{file_id}_chunk_{chunk_index}"
            chunk_path = os.path.join(node_path, chunk_filename)

            with open(chunk_path, "wb") as f:
                f.write(chunk_data)

            chunk_paths.append(chunk_path)

        chunk_metadata.append({
            "chunk_index": chunk_index,
            "chunk_hash": chunk_hash,
            "chunk_paths": chunk_paths
        })

        chunk_index += 1

    db.close()

    return total_size, chunk_index, chunk_metadata

