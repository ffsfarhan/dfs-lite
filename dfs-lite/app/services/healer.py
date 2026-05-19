import os
import time
import shutil
import threading

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.chunk import Chunk
from app.models.node import Node

# --------------------------------------------------
# Storage Root
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

# --------------------------------------------------
# Self-Healing Logic
# --------------------------------------------------
def heal_missing_chunks():

    while True:

        print("\n[HEALER] Scanning replicas...")

        db: Session = SessionLocal()

        try:

            chunks = db.query(Chunk).all()

            for chunk in chunks:

                expected_path = chunk.chunk_path

                # If chunk exists -> OK
                if os.path.exists(expected_path):
                    continue

                print(
                    "[HEALER] Missing chunk:",
                    expected_path
                )

                filename = os.path.basename(
                    expected_path
                )

                # Search healthy replicas
                source_path = None

                for node_name in [
                    "node1",
                    "node2",
                    "node3"
                ]:

                    possible_path = os.path.join(
                        STORAGE_DIR,
                        node_name,
                        filename
                    )

                    if os.path.exists(possible_path):

                        source_path = possible_path
                        break

                # Restore replica
                if source_path:

                    print(
                        "[HEALER] Restoring from:",
                        source_path
                    )

                    os.makedirs(
                        os.path.dirname(expected_path),
                        exist_ok=True
                    )

                    shutil.copy2(
                        source_path,
                        expected_path
                    )

                    print(
                        "[HEALER] Replica restored:",
                        expected_path
                    )

        except Exception as e:

            print("[HEALER ERROR]", str(e))

        finally:

            db.close()

        # Scan every 10 seconds
        time.sleep(10)


# --------------------------------------------------
# Start Background Healer
# --------------------------------------------------
def start_healer():

    thread = threading.Thread(
        target=heal_missing_chunks,
        daemon=True
    )

    thread.start()

    print("[HEALER] Background healer started")
