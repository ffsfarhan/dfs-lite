from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.node import Node
from app.models.file import File

router = APIRouter(prefix="/cluster", tags=["Cluster"])


@router.get("/health")
def cluster_health(db: Session = Depends(get_db)):

    total_nodes = db.query(func.count(Node.id)).scalar()
    online_nodes = db.query(func.count(Node.id)).filter(Node.is_online == True).scalar()
    offline_nodes = total_nodes - online_nodes

    total_files = db.query(func.count(File.id)).scalar()

    healthy_files = db.query(func.count(File.id)).filter(File.status == "HEALTHY").scalar()
    degraded_files = db.query(func.count(File.id)).filter(File.status == "DEGRADED").scalar()
    dead_files = db.query(func.count(File.id)).filter(File.status == "DEAD").scalar()

    # Determine cluster state
    if dead_files > 0:
        cluster_state = "CRITICAL"
    elif degraded_files > 0:
        cluster_state = "DEGRADED"
    else:
        cluster_state = "HEALTHY"

    return {
        "nodes": {
            "total": total_nodes,
            "online": online_nodes,
            "offline": offline_nodes
        },
        "files": {
            "total": total_files,
            "healthy": healthy_files,
            "degraded": degraded_files,
            "dead": dead_files
        },
        "cluster_status": cluster_state
    }
