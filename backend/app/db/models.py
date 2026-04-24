from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    asset_type = Column(String(10), nullable=False)  # "STOCK" or "MF"
    quantity = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    sector = Column(String(100), default="")
    imported_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), nullable=False, index=True)
    role = Column(String(10), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    action = Column(String(10), nullable=False)  # "BUY", "SELL", "HOLD"
    rationale = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    notes = Column(Text, default="")
    added_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


class AnalysisSnapshot(Base):
    __tablename__ = "analysis_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_type = Column(String(50), nullable=False)  # "daily", "weekly"
    content = Column(Text, nullable=False)  # JSON blob
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
