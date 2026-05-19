import os

class Settings:
    # Replication factor (how many replicas per chunk)
    REPLICATION_FACTOR = int(os.getenv("REPLICATION_FACTOR", 2))

    # Storage nodes (simulating distributed machines)
    STORAGE_NODES = [
        "storage/node1",
        "storage/node2",
        "storage/node3",
    ]

settings = Settings()

