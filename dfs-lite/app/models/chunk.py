from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"))
    chunk_index = Column(Integer, nullable=False)
    chunk_hash = Column(String, nullable=False)
    chunk_path = Column(String, nullable=False)

