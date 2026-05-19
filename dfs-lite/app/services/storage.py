import os
import hashlib

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.node import Node

CHUNK_SIZE = 1024 * 1024  # 1 MB


# --------------------------------------------------
# REAL PROJECT ROOT
# storage.py -> services -> app -> dfs-lite
# --------------------------------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

STORAGE_DIR = os.path.join(
    BASE_DIR,
    "storage"
)

print("BASE_DIR =", BASE_DIR)
print("STORAGE_DIR =", STORAGE_DIR)


# --------------------------------------------------
# SAVE FILE IN CHUNKS
# --------------------------------------------------
def save_file_in_chunks(file, file_id):

    db: Session = SessionLocal()

    try:

        # Get ONLINE nodes from database
        online_nodes = db.query(Node).filter(
            Node.is_online == True
        ).all()

        print(
            "ONLINE NODES:",
            [node.name for node in online_nodes]
        )

        # No nodes available
        if not online_nodes:
            raise Exception(
                "No storage nodes online"
            )

        total_size = 0
        total_chunks = 0

        chunk_metadata = []

        chunk_index = 0

        while True:

            chunk_data = file.read(CHUNK_SIZE)

            # EOF
            if not chunk_data:
                break

            print(
                f"\nPROCESSING CHUNK {chunk_index}"
            )

            total_size += len(chunk_data)

            chunk_hash = hashlib.sha256(
                chunk_data
            ).hexdigest()

            chunk_paths = []

            # Replicate ONLY to online nodes
            for node in online_nodes:

                node_path = os.path.join(
                    STORAGE_DIR,
                    node.name
                )

                os.makedirs(
                    node_path,
                    exist_ok=True
                )

                chunk_filename = (
                    f"{file_id}_chunk_{chunk_index}"
                )

                chunk_path = os.path.join(
                    node_path,
                    chunk_filename
                )

                print(
                    "WRITING TO:",
                    chunk_path
                )

                with open(chunk_path, "wb") as f:
                    f.write(chunk_data)

                print(
                    "WRITE SUCCESS:",
                    os.path.exists(chunk_path)
                )

                chunk_paths.append(chunk_path)

            chunk_metadata.append({
                "chunk_index": chunk_index,
                "chunk_hash": chunk_hash,
                "chunk_paths": chunk_paths
            })

            total_chunks += 1
            chunk_index += 1

        return (
            total_size,
            total_chunks,
            chunk_metadata
        )

    finally:

        db.close()
