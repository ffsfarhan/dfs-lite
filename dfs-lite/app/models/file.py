from sqlalchemy import Column, String, BigInteger, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    total_size = Column(BigInteger, nullable=False)
    total_chunks = Column(Integer, nullable=False)
    status = Column(String, default="HEALTHY")  # NEW FIELD
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

