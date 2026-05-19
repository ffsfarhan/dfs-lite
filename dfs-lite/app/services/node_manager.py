from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.node import Node
from app.config import settings


def initialize_nodes():

    db: Session = SessionLocal()

    try:
        for node_path in settings.STORAGE_NODES:

            node_name = node_path.split("/")[-1]

            existing = db.query(Node).filter(Node.name == node_name).first()

            if not existing:
                node = Node(
                     name=node_name,
                     path=node_path,
                     is_online=True
                )

                db.add(node)
            else:
                existing.status = "ACTIVE"

        db.commit()

    finally:
        db.close()

