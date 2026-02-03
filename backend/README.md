# Backend (FastAPI)

This service provides the API for clients, tickers, currencies, and audit logs.

## Suggested setup
1. Create a virtualenv
   - `python -m venv .venv`
2. Activate it
   - macOS: `source .venv/bin/activate`
3. Install dependencies
   - `pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic`
4. Create a PostgreSQL database and set `DATABASE_URL`.
   - Example: `postgresql://user:pass@localhost:5432/client_tool`
5. Run the app
   - `uvicorn app.main:app --reload`

## Environment
- `DATABASE_URL` (required)
- `APP_ENV` (optional, defaults to `dev`)

## Schema
See `schema.sql` for the proposed database tables.
