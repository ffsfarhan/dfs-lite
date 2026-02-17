import os
import hashlib
import random
from app.config import settings

CHUNK_SIZE = 1024 * 1024  # 1MB per chunk


def save_file_in_chunks(file_obj, file_id):

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

        # Select storage nodes dynamically based on replication factor
        selected_nodes = random.sample(
            settings.STORAGE_NODES,
            settings.REPLICATION_FACTOR
        )

        chunk_paths = []

        for node in selected_nodes:

            os.makedirs(node, exist_ok=True)

            chunk_filename = f"{file_id}_chunk_{chunk_index}"
            chunk_path = os.path.join(node, chunk_filename)

            with open(chunk_path, "wb") as f:
                f.write(chunk_data)

            chunk_paths.append(chunk_path)

        chunk_metadata.append({
            "chunk_index": chunk_index,
            "chunk_hash": chunk_hash,
            "chunk_paths": chunk_paths
        })

        chunk_index += 1

    return total_size, chunk_index, chunk_metadata

