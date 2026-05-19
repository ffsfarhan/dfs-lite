import os
import time
import hashlib
import random

from sqlalchemy.orm import Session
from collections import defaultdict

from app.database import SessionLocal
from app.models.chunk import Chunk
from app.models.file import File
from app.models.node import Node
from app.config import settings


def repair_daemon():

    while True:
        print("[REPAIR] Running background scan...")

        db: Session = SessionLocal()

        try:
            files = db.query(File).all()

            for file in files:

                chunks = (
                    db.query(Chunk)
                    .filter(Chunk.file_id == file.id)
                    .order_by(Chunk.chunk_index)
                    .all()
                )

                chunk_groups = defaultdict(list)
                for c in chunks:
                    chunk_groups[c.chunk_index].append(c)

                for chunk_index, replicas in chunk_groups.items():

                    valid_data = None
                    valid_hash = None

                    # ------------- Find healthy replica -------------
                    for replica in replicas:
                        if not os.path.exists(replica.chunk_path):
                            continue

                        with open(replica.chunk_path, "rb") as f:
                            data = f.read()

                        computed = hashlib.sha256(data).hexdigest()

                        if computed == replica.chunk_hash:
                            valid_data = data
                            valid_hash = computed
                            break

                    if not valid_data:
                        print(f"[REPAIR] All replicas corrupted for {file.id} chunk {chunk_index}")
                        file.status = "DEAD"
                        continue

                    # ------------- Remove missing replicas from DB -------------
                    for replica in replicas:
                        if not os.path.exists(replica.chunk_path):
                            db.delete(replica)

                    db.commit()

                    # Refresh replicas list
                    replicas = (
                        db.query(Chunk)
                        .filter(Chunk.file_id == file.id)
                        .filter(Chunk.chunk_index == chunk_index)
                        .all()
                    )

                    # ------------- Ensure replication factor -------------
                    active_nodes = db.query(Node).all()
                    existing_paths = [r.chunk_path for r in replicas]

                    while len(replicas) < settings.REPLICATION_FACTOR:

                        node = random.choice(active_nodes)

                        new_path = os.path.join(
                            node.path,
                            f"{file.id}_chunk_{chunk_index}"
                        )

                        if new_path in existing_paths:
                            continue

                        with open(new_path, "wb") as f:
                            f.write(valid_data)

                        new_chunk = Chunk(
                            file_id=file.id,
                            chunk_index=chunk_index,
                            chunk_hash=valid_hash,
                            chunk_path=new_path
                        )

                        db.add(new_chunk)
                        db.commit()

                        replicas.append(new_chunk)
                        existing_paths.append(new_path)

                        print(f"[REPAIR] Recreated replica on {node.name}")

                    file.status = "HEALTHY"

                db.commit()

        finally:
            db.close()

        time.sleep(15)

