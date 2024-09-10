import uuid
from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_name = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)