"""
CivicLens — SQLAlchemy ORM Models
Maps Python classes to the MySQL tables defined in schema.sql
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.utils.database import Base


class Dataset(Base):
    """Tracks each uploaded file."""
    __tablename__ = "datasets"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(255), nullable=False)
    filename    = Column(String(255), nullable=False)
    row_count   = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status      = Column(String(50), default="pending")

    records     = relationship("OperationalRecord", back_populates="dataset", cascade="all, delete")
    quality_log = relationship("DataQualityLog", back_populates="dataset", cascade="all, delete")


class OperationalRecord(Base):
    """One cleaned data row from an uploaded file."""
    __tablename__ = "operational_records"

    id                  = Column(Integer, primary_key=True, index=True)
    dataset_id          = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"))
    record_date         = Column(Date)
    location            = Column(String(255))
    program_type        = Column(String(255))
    clients_served      = Column(Integer)
    meals_distributed   = Column(Integer)
    inventory_lbs       = Column(Numeric(10, 2))
    volunteer_hours     = Column(Numeric(8, 2))
    zip_code            = Column(String(20))
    notes               = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="records")


class DataQualityLog(Base):
    """Validation issues flagged during cleaning."""
    __tablename__ = "data_quality_log"

    id          = Column(Integer, primary_key=True, index=True)
    dataset_id  = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"))
    issue_type  = Column(String(100))
    column_name = Column(String(100))
    row_index   = Column(Integer)
    detail      = Column(Text)
    flagged_at  = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="quality_log")


class ClaudeQuery(Base):
    """Log of all Claude API calls."""
    __tablename__ = "claude_queries"

    id              = Column(Integer, primary_key=True, index=True)
    dataset_id      = Column(Integer, ForeignKey("datasets.id"))
    query_type      = Column(String(50))
    user_prompt     = Column(Text)
    claude_response = Column(Text)
    created_at      = Column(DateTime, default=datetime.utcnow)
