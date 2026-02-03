-- Core tables
CREATE TABLE clients (
  id UUID PRIMARY KEY,
  client_name TEXT NOT NULL,
  tenors_min TEXT,
  tenors_max TEXT,
  tenors_sweetspot TEXT,
  frn_buyer BOOLEAN DEFAULT FALSE,
  callable_buyer BOOLEAN DEFAULT FALSE,
  private_placement_buyer TEXT,
  esg_green BOOLEAN DEFAULT FALSE,
  esg_social BOOLEAN DEFAULT FALSE,
  esg_sustainable BOOLEAN DEFAULT FALSE,
  target_spread_ois TEXT,
  target_g_spread TEXT,
  toms_code TEXT,
  client_notes TEXT,
  region TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tickers (
  id UUID PRIMARY KEY,
  symbol TEXT NOT NULL UNIQUE
);

CREATE TABLE currencies (
  id UUID PRIMARY KEY,
  code TEXT NOT NULL UNIQUE
);

-- Many-to-many relationships
CREATE TABLE client_tickers (
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  ticker_id UUID NOT NULL REFERENCES tickers(id) ON DELETE CASCADE,
  PRIMARY KEY (client_id, ticker_id)
);

CREATE TABLE client_currencies (
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  currency_id UUID NOT NULL REFERENCES currencies(id) ON DELETE CASCADE,
  PRIMARY KEY (client_id, currency_id)
);

-- Audit log
CREATE TABLE audit_log (
  id UUID PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  user_id UUID,
  field_name TEXT NOT NULL,
  old_value TEXT,
  new_value TEXT,
  changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_client_name ON clients (client_name);
CREATE INDEX idx_ticker_symbol ON tickers (symbol);
CREATE INDEX idx_currency_code ON currencies (code);
CREATE INDEX idx_audit_client ON audit_log (client_id, changed_at);
