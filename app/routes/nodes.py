from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.node import Node

router = APIRouter(prefix="/nodes", tags=["Nodes"])


# -----------------------------------------
# LIST NODES
# GET /nodes
# -----------------------------------------
@router.get("")
def list_nodes(db: Session = Depends(get_db)):
    nodes = db.query(Node).order_by(Node.name).all()


    return [
        {
            "name": node.name,
            "path": node.path,
            "is_online": node.is_online,
        }
        for node in nodes
    ]


# -----------------------------------------
# TOGGLE NODE ONLINE/OFFLINE
# POST /nodes/{node_name}/toggle
# -----------------------------------------
@router.post("/{node_name}/toggle")
def toggle_node(node_name: str, db: Session = Depends(get_db)):

    node = db.query(Node).filter(Node.name == node_name).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    node.is_online = not node.is_online
    db.commit()

    return {
        "message": "Node toggled successfully",
        "node": node.name,
        "is_online": node.is_online,
    }

