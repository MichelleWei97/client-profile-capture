from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from typing import Optional, List, Iterable

from .db import get_db_session
from .models import Client, Ticker, Currency, AuditLog
from .schemas import (
    ClientListResponse,
    ClientOut,
    ClientUpdate,
    ClientCreate,
    AuditListResponse,
    AuditItem,
)

app = FastAPI(title="Client Tool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

def _normalize_list(values: Optional[Iterable[str]]) -> List[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = values.split(",")
    cleaned = []
    for value in values:
        if value is None:
            continue
        item = value.strip()
        if not item:
            continue
        cleaned.append(item.upper())
    return cleaned


@app.get("/clients", response_model=ClientListResponse)
def list_clients(
    q: Optional[str] = Query(None, description="Text search across client name and tickers"),
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol(s), comma-separated"),
    currency: Optional[str] = Query(None, description="Filter by currency code(s), comma-separated"),
):
    with get_db_session() as session:
        query = session.query(Client).options(
            joinedload(Client.tickers),
            joinedload(Client.currencies),
        )

        if ticker:
            tickers = _normalize_list(ticker)
            if tickers:
                query = (
                    query.join(Client.tickers)
                    .filter(Ticker.symbol.in_(tickers))
                    .group_by(Client.id)
                    .having(func.count(func.distinct(Ticker.id)) >= len(tickers))
                )
        if currency:
            currencies = _normalize_list(currency)
            if currencies:
                query = (
                    query.join(Client.currencies)
                    .filter(Currency.code.in_(currencies))
                    .group_by(Client.id)
                    .having(func.count(func.distinct(Currency.id)) >= len(currencies))
                )
        if q:
            q_like = f"%{q}%"
            query = query.outerjoin(Client.tickers).filter(
                (Client.client_name.ilike(q_like)) | (Ticker.symbol.ilike(q_like))
            )

        clients = query.distinct().all()

        items = []
        for client in clients:
            items.append(
                ClientOut(
                    id=str(client.id),
                    client_name=client.client_name,
                    tickers=[t.symbol for t in client.tickers],
                    currencies=[c.code for c in client.currencies],
                    tenors_min=client.tenors_min,
                    tenors_max=client.tenors_max,
                    tenors_sweetspot=client.tenors_sweetspot,
                    frn_buyer=client.frn_buyer,
                    callable_buyer=client.callable_buyer,
                    private_placement_buyer=client.private_placement_buyer,
                    esg_green=client.esg_green,
                    esg_social=client.esg_social,
                    esg_sustainable=client.esg_sustainable,
                    target_spread_ois=client.target_spread_ois,
                    target_g_spread=client.target_g_spread,
                    toms_code=client.toms_code,
                    client_notes=client.client_notes,
                    region=client.region,
                )
            )
        return ClientListResponse(items=items)

@app.post("/clients", response_model=ClientOut, status_code=201)
def create_client(payload: ClientCreate):
    with get_db_session() as session:
        client = Client(
            client_name=payload.client_name,
            tenors_min=payload.tenors_min,
            tenors_max=payload.tenors_max,
            tenors_sweetspot=payload.tenors_sweetspot,
            frn_buyer=payload.frn_buyer or False,
            callable_buyer=payload.callable_buyer or False,
            private_placement_buyer=payload.private_placement_buyer,
            esg_green=payload.esg_green or False,
            esg_social=payload.esg_social or False,
            esg_sustainable=payload.esg_sustainable or False,
            target_spread_ois=payload.target_spread_ois,
            target_g_spread=payload.target_g_spread,
            toms_code=payload.toms_code,
            client_notes=payload.client_notes,
            region=payload.region,
        )

        if payload.tickers is not None:
            symbols = _normalize_list(payload.tickers)
            ticker_models = []
            for symbol in symbols:
                existing = session.query(Ticker).filter(Ticker.symbol == symbol).first()
                if not existing:
                    existing = Ticker(symbol=symbol)
                    session.add(existing)
                ticker_models.append(existing)
            client.tickers = ticker_models

        if payload.currencies is not None:
            codes = _normalize_list(payload.currencies)
            currency_models = []
            for code in codes:
                existing = session.query(Currency).filter(Currency.code == code).first()
                if not existing:
                    existing = Currency(code=code)
                    session.add(existing)
                currency_models.append(existing)
            client.currencies = currency_models

        session.add(client)
        session.commit()
        session.refresh(client)

        return ClientOut(
            id=str(client.id),
            client_name=client.client_name,
            tickers=[t.symbol for t in client.tickers],
            currencies=[c.code for c in client.currencies],
            tenors_min=client.tenors_min,
            tenors_max=client.tenors_max,
            tenors_sweetspot=client.tenors_sweetspot,
            frn_buyer=client.frn_buyer,
            callable_buyer=client.callable_buyer,
            private_placement_buyer=client.private_placement_buyer,
            esg_green=client.esg_green,
            esg_social=client.esg_social,
            esg_sustainable=client.esg_sustainable,
            target_spread_ois=client.target_spread_ois,
            target_g_spread=client.target_g_spread,
            toms_code=client.toms_code,
            client_notes=client.client_notes,
            region=client.region,
        )

@app.patch("/clients/{client_id}", response_model=ClientOut)
def update_client(client_id: str, payload: ClientUpdate):
    with get_db_session() as session:
        client = (
            session.query(Client)
            .options(joinedload(Client.tickers), joinedload(Client.currencies))
            .filter(Client.id == client_id)
            .first()
        )
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        changed_fields = []

        # Scalar fields
        for field_name, new_value in payload.model_dump(exclude_none=True).items():
            if field_name in {"tickers", "currencies"}:
                continue
            old_value = getattr(client, field_name)
            if new_value != old_value:
                setattr(client, field_name, new_value)
                changed_fields.append((field_name, old_value, new_value))

        # Tickers
        if payload.tickers is not None:
            new_tickers = _normalize_list(payload.tickers)
            old_tickers = [t.symbol for t in client.tickers]
            if sorted(new_tickers) != sorted(old_tickers):
                ticker_models = []
                for symbol in new_tickers:
                    existing = session.query(Ticker).filter(Ticker.symbol == symbol).first()
                    if not existing:
                        existing = Ticker(symbol=symbol)
                        session.add(existing)
                    ticker_models.append(existing)
                client.tickers = ticker_models
                changed_fields.append(("tickers", ", ".join(old_tickers), ", ".join(new_tickers)))

        # Currencies
        if payload.currencies is not None:
            new_currencies = _normalize_list(payload.currencies)
            old_currencies = [c.code for c in client.currencies]
            if sorted(new_currencies) != sorted(old_currencies):
                currency_models = []
                for code in new_currencies:
                    existing = session.query(Currency).filter(Currency.code == code).first()
                    if not existing:
                        existing = Currency(code=code)
                        session.add(existing)
                    currency_models.append(existing)
                client.currencies = currency_models
                changed_fields.append(
                    ("currencies", ", ".join(old_currencies), ", ".join(new_currencies))
                )

        for field_name, old_value, new_value in changed_fields:
            session.add(
                AuditLog(
                    client_id=client.id,
                    user_id=None,
                    field_name=field_name,
                    old_value=None if old_value is None else str(old_value),
                    new_value=None if new_value is None else str(new_value),
                )
            )

        session.commit()
        session.refresh(client)

        return ClientOut(
            id=str(client.id),
            client_name=client.client_name,
            tickers=[t.symbol for t in client.tickers],
            currencies=[c.code for c in client.currencies],
            tenors_min=client.tenors_min,
            tenors_max=client.tenors_max,
            tenors_sweetspot=client.tenors_sweetspot,
            frn_buyer=client.frn_buyer,
            callable_buyer=client.callable_buyer,
            private_placement_buyer=client.private_placement_buyer,
            esg_green=client.esg_green,
            esg_social=client.esg_social,
            esg_sustainable=client.esg_sustainable,
            target_spread_ois=client.target_spread_ois,
            target_g_spread=client.target_g_spread,
            toms_code=client.toms_code,
            client_notes=client.client_notes,
            region=client.region,
        )

@app.get("/clients/{client_id}/audit", response_model=AuditListResponse)
def client_audit(client_id: str):
    with get_db_session() as session:
        items = (
            session.query(AuditLog)
            .filter(AuditLog.client_id == client_id)
            .order_by(AuditLog.changed_at.desc())
            .all()
        )
        return AuditListResponse(
            items=[
                AuditItem(
                    id=str(item.id),
                    client_id=str(item.client_id),
                    user_id=str(item.user_id) if item.user_id else None,
                    field_name=item.field_name,
                    old_value=item.old_value,
                    new_value=item.new_value,
                    changed_at=item.changed_at.isoformat(),
                )
                for item in items
            ]
        )
