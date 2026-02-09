import os
from typing import List

from app.db import get_db_session
from app.models import Client, Ticker, Currency


def _normalize(values: List[str]) -> List[str]:
    cleaned = []
    seen = set()
    for value in values:
        if not value:
            continue
        item = value.strip().upper()
        if not item or item in seen:
            continue
        seen.add(item)
        cleaned.append(item)
    return cleaned


def _get_or_create_tickers(session, symbols: List[str]) -> List[Ticker]:
    tickers = []
    for symbol in _normalize(symbols):
        existing = session.query(Ticker).filter(Ticker.symbol == symbol).first()
        if not existing:
            existing = Ticker(symbol=symbol)
            session.add(existing)
        tickers.append(existing)
    return tickers


def _get_or_create_currencies(session, codes: List[str]) -> List[Currency]:
    currencies = []
    for code in _normalize(codes):
        existing = session.query(Currency).filter(Currency.code == code).first()
        if not existing:
            existing = Currency(code=code)
            session.add(existing)
        currencies.append(existing)
    return currencies


def seed():
    sample_clients = [
        {
            "client_name": "RBIB",
            "tickers": ["AAPL", "MSFT"],
            "currencies": ["CAD", "GBP"],
            "tenors_min": "2Y",
            "tenors_max": "10Y",
            "tenors_sweetspot": "5Y",
            "frn_buyer": True,
            "callable_buyer": False,
            "private_placement_buyer": "Yes",
            "esg_green": True,
            "esg_social": False,
            "esg_sustainable": False,
            "target_spread_ois": "OIS+110",
            "target_g_spread": "G+140",
            "toms_code": "RBIB-01",
            "client_notes": "Prefers high quality issuers.",
            "region": "NA",
        },
        {
            "client_name": "Blue Harbor",
            "tickers": ["TSLA"],
            "currencies": ["USD"],
            "tenors_min": "1Y",
            "tenors_max": "7Y",
            "tenors_sweetspot": "3Y",
            "frn_buyer": False,
            "callable_buyer": True,
            "private_placement_buyer": "No",
            "esg_green": False,
            "esg_social": True,
            "esg_sustainable": True,
            "target_spread_ois": "OIS+90",
            "target_g_spread": "G+120",
            "toms_code": "BH-88",
            "client_notes": "Likes callable structures.",
            "region": "US",
        },
        {
            "client_name": "Northwind Capital",
            "tickers": ["NVDA", "AAPL"],
            "currencies": ["EUR", "USD"],
            "tenors_min": "3Y",
            "tenors_max": "12Y",
            "tenors_sweetspot": "7Y",
            "frn_buyer": True,
            "callable_buyer": True,
            "private_placement_buyer": "Maybe",
            "esg_green": True,
            "esg_social": True,
            "esg_sustainable": False,
            "target_spread_ois": "OIS+130",
            "target_g_spread": "G+160",
            "toms_code": "NWC-12",
            "client_notes": "Sensitive to spread volatility.",
            "region": "EU",
        },
    ]

    with get_db_session() as session:
        for data in sample_clients:
            existing = (
                session.query(Client)
                .filter(Client.client_name == data["client_name"])
                .first()
            )
            if existing:
                continue

            client = Client(
                client_name=data["client_name"],
                tenors_min=data["tenors_min"],
                tenors_max=data["tenors_max"],
                tenors_sweetspot=data["tenors_sweetspot"],
                frn_buyer=data["frn_buyer"],
                callable_buyer=data["callable_buyer"],
                private_placement_buyer=data["private_placement_buyer"],
                esg_green=data["esg_green"],
                esg_social=data["esg_social"],
                esg_sustainable=data["esg_sustainable"],
                target_spread_ois=data["target_spread_ois"],
                target_g_spread=data["target_g_spread"],
                toms_code=data["toms_code"],
                client_notes=data["client_notes"],
                region=data["region"],
            )

            client.tickers = _get_or_create_tickers(session, data["tickers"])
            client.currencies = _get_or_create_currencies(session, data["currencies"])
            session.add(client)

        session.commit()


if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        raise SystemExit("DATABASE_URL is not set")
    seed()
    print("Seed complete.")
