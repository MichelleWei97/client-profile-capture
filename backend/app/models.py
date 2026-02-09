import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_name = Column(Text, nullable=False)
    tenors_min = Column(Text)
    tenors_max = Column(Text)
    tenors_sweetspot = Column(Text)
    frn_buyer = Column(Boolean, default=False)
    callable_buyer = Column(Boolean, default=False)
    private_placement_buyer = Column(Text)
    esg_green = Column(Boolean, default=False)
    esg_social = Column(Boolean, default=False)
    esg_sustainable = Column(Boolean, default=False)
    target_spread_ois = Column(Text)
    target_g_spread = Column(Text)
    toms_code = Column(Text)
    client_notes = Column(Text)
    region = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tickers = relationship("Ticker", secondary="client_tickers", back_populates="clients")
    currencies = relationship("Currency", secondary="client_currencies", back_populates="clients")


class Ticker(Base):
    __tablename__ = "tickers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(Text, nullable=False, unique=True)

    clients = relationship("Client", secondary="client_tickers", back_populates="tickers")


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(Text, nullable=False, unique=True)

    clients = relationship("Client", secondary="client_currencies", back_populates="currencies")


class ClientTicker(Base):
    __tablename__ = "client_tickers"

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), primary_key=True)
    ticker_id = Column(UUID(as_uuid=True), ForeignKey("tickers.id", ondelete="CASCADE"), primary_key=True)


class ClientCurrency(Base):
    __tablename__ = "client_currencies"

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), primary_key=True)
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currencies.id", ondelete="CASCADE"), primary_key=True)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True))
    field_name = Column(Text, nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
