import os
import time
import shutil
import hashlib
import threading

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.chunk import Chunk

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
# Calculate SHA256
# --------------------------------------------------
def calculate_sha256(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:

        while True:

            data = f.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


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
                expected_hash = chunk.chunk_hash

                filename = os.path.basename(
                    expected_path
                )

                # --------------------------------------------------
                # CASE 1: Missing Replica
                # --------------------------------------------------
                if not os.path.exists(expected_path):

                    print(
                        "[HEALER] Missing chunk:",
                        expected_path
                    )

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

                            # Verify healthy replica
                            current_hash = calculate_sha256(
                                possible_path
                            )

                            if current_hash == expected_hash:

                                source_path = possible_path
                                break

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

                # --------------------------------------------------
                # CASE 2: Corrupted Replica
                # --------------------------------------------------
                else:

                    current_hash = calculate_sha256(
                        expected_path
                    )

                    if current_hash != expected_hash:

                        print(
                            "[HEALER] CORRUPTION DETECTED:",
                            expected_path
                        )

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

                            if (
                                os.path.exists(possible_path)
                                and possible_path != expected_path
                            ):

                                replica_hash = calculate_sha256(
                                    possible_path
                                )

                                if replica_hash == expected_hash:

                                    source_path = possible_path
                                    break

                        if source_path:

                            print(
                                "[HEALER] Replacing corrupted replica using:",
                                source_path
                            )

                            os.remove(expected_path)

                            shutil.copy2(
                                source_path,
                                expected_path
                            )

                            print(
                                "[HEALER] Corrupted replica repaired:",
                                expected_path
                            )

        except Exception as e:

            print(
                "[HEALER ERROR]",
                str(e)
            )

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

    print(
        "[HEALER] Background healer started"
    )
