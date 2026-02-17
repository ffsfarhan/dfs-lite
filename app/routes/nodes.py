from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.node import Node

router = APIRouter(prefix="/nodes", tags=["Nodes"])


# ----------------------------------------
# List All Nodes
# ----------------------------------------
@router.get("/")
def list_nodes(db: Session = Depends(get_db)):

    nodes = db.query(Node).all()

    return [
        {
            "id": node.id,
            "name": node.name,
            "path": node.path,
            "is_online": node.is_online
        }
        for node in nodes
    ]


# ----------------------------------------
# Simulate Node Failure (OFFLINE)
# ----------------------------------------
@router.post("/{node_id}/offline")
def set_node_offline(node_id: int, db: Session = Depends(get_db)):

    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    node.is_online = False
    db.commit()

    return {"message": f"Node {node.name} is now OFFLINE"}


# ----------------------------------------
# Bring Node Back Online
# ----------------------------------------
@router.post("/{node_id}/online")
def set_node_online(node_id: int, db: Session = Depends(get_db)):

    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    node.is_online = True
    db.commit()

    return {"message": f"Node {node.name} is now ONLINE"}

