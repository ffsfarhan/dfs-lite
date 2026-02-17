from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    path = Column(String, unique=True, nullable=False)
    is_online = Column(Boolean, default=True)

