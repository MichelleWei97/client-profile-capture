from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(title="Client Tool API")

@app.get("/health")
def health():
    return {"ok": True}

# TODO: Implement database-backed handlers
@app.get("/clients")
def list_clients(
    q: Optional[str] = Query(None, description="Text search across client name and tickers"),
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    currency: Optional[str] = Query(None, description="Filter by currency code"),
):
    return {
        "items": [],
        "filters": {"q": q, "ticker": ticker, "currency": currency},
    }

@app.patch("/clients/{client_id}")
def update_client(client_id: str):
    return {"id": client_id, "updated": False}

@app.get("/clients/{client_id}/audit")
def client_audit(client_id: str):
    return {"id": client_id, "items": []}
