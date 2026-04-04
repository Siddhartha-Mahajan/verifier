from sqlalchemy import Boolean, Column, DateTime, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
	pass


class Submission(Base):
	__tablename__ = "submissions"

	submission_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
	created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
	email = Column(String(255), nullable=False)
	ip_address = Column(String(45), nullable=False)
	problem_name = Column(String(32), nullable=False, index=True)
	instance = Column(JSONB, nullable=False)
	submission = Column(JSONB, nullable=False)
	is_valid = Column(Boolean, nullable=False)
	score = Column(Numeric, nullable=True, index=True)
	score_direction = Column(String(4), nullable=False)
	error_message = Column(Text, nullable=True)
	percentile = Column(Numeric, nullable=True)
	is_record = Column(Boolean, nullable=False, default=False)