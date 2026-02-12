import { useEffect, useMemo, useState } from 'react'
import './App.css'

type Client = {
  id: string
  client_name: string
  tickers: string[]
  currencies: string[]
  tenors_min: string | null
  tenors_max: string | null
  tenors_sweetspot: string | null
  frn_buyer: boolean
  callable_buyer: boolean
  private_placement_buyer: string | null
  esg_green: boolean
  esg_social: boolean
  esg_sustainable: boolean
  target_spread_ois: string | null
  target_g_spread: string | null
  toms_code: string | null
  client_notes: string | null
  region: string | null
}

type FilterState = {
  q: string
  ticker: string
  currency: string
}

type AuditItem = {
  id: string
  client_id: string
  user_id?: string | null
  field_name: string
  old_value?: string | null
  new_value?: string | null
  changed_at: string
}

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'

const parseList = (value: string) =>
  value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)

const formatList = (values: string[]) => values.join(', ')

const applyDropdownSelection = (current: string, nextValue: string) => {
  const parts = current.split(',')
  if (parts.length <= 1) {
    return nextValue
  }
  parts[parts.length - 1] = ` ${nextValue}`
  return parts.join(',').replace(/\s*,\s*/g, ', ')
}

const columnLabels: { key: keyof Client; label: string; type: 'text' | 'boolean' }[] = [
  { key: 'client_name', label: 'Client Name', type: 'text' },
  { key: 'tickers', label: 'Tickers', type: 'text' },
  { key: 'currencies', label: 'Currencies', type: 'text' },
  { key: 'tenors_min', label: 'Tenors Min', type: 'text' },
  { key: 'tenors_max', label: 'Tenors Max', type: 'text' },
  { key: 'tenors_sweetspot', label: 'Tenors SweetSpot', type: 'text' },
  { key: 'frn_buyer', label: 'FRN Buyer', type: 'boolean' },
  { key: 'callable_buyer', label: 'Callable Buyer', type: 'boolean' },
  { key: 'private_placement_buyer', label: 'Private Placement Buyer', type: 'text' },
  { key: 'esg_green', label: 'ESG Green', type: 'boolean' },
  { key: 'esg_social', label: 'ESG Social', type: 'boolean' },
  { key: 'esg_sustainable', label: 'ESG Sustainable', type: 'boolean' },
  { key: 'target_spread_ois', label: 'Target Spread OIS', type: 'text' },
  { key: 'target_g_spread', label: 'Target G-Spread', type: 'text' },
  { key: 'toms_code', label: "TOM's Code", type: 'text' },
  { key: 'client_notes', label: 'Client Notes', type: 'text' },
  { key: 'region', label: 'Region', type: 'text' },
]

function App() {
  const [clients, setClients] = useState<Client[]>([])
  const [filters, setFilters] = useState<FilterState>({ q: '', ticker: '', currency: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editBuffer, setEditBuffer] = useState<Record<string, string>>({})
  const [selectedClientId, setSelectedClientId] = useState<string | null>(null)
  const [auditItems, setAuditItems] = useState<AuditItem[]>([])
  const [auditLoading, setAuditLoading] = useState(false)
  const [createOpen, setCreateOpen] = useState(false)
  const [createForm, setCreateForm] = useState({
    client_name: '',
    tickers: '',
    currencies: '',
    region: '',
  })
  const [tickerOpen, setTickerOpen] = useState(false)
  const [currencyOpen, setCurrencyOpen] = useState(false)

  const uniqueTickers = useMemo(() => {
    const set = new Set<string>()
    clients.forEach((client) => client.tickers.forEach((ticker) => set.add(ticker)))
    return Array.from(set).sort()
  }, [clients])

  const uniqueCurrencies = useMemo(() => {
    const set = new Set<string>()
    clients.forEach((client) => client.currencies.forEach((currency) => set.add(currency)))
    return Array.from(set).sort()
  }, [clients])

  const fetchClients = async (override?: Partial<FilterState>) => {
    setLoading(true)
    setError(null)
    try {
      const nextFilters = { ...filters, ...override }
      const params = new URLSearchParams()
      if (nextFilters.q) params.set('q', nextFilters.q)
      if (nextFilters.ticker) params.set('ticker', nextFilters.ticker)
      if (nextFilters.currency) params.set('currency', nextFilters.currency)

      const response = await fetch(`${API_BASE}/clients?${params.toString()}`)
      if (!response.ok) {
        throw new Error('Failed to load clients.')
      }
      const data = await response.json()
      setClients(data.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error.')
    } finally {
      setLoading(false)
    }
  }

  const fetchAudit = async (clientId: string) => {
    setAuditLoading(true)
    try {
      const response = await fetch(`${API_BASE}/clients/${clientId}/audit`)
      if (!response.ok) {
        throw new Error('Failed to load audit history.')
      }
      const data = await response.json()
      setAuditItems(data.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load audit history.')
      setAuditItems([])
    } finally {
      setAuditLoading(false)
    }
  }

  useEffect(() => {
    fetchClients()
  }, [])

  const updateClient = async (client: Client, field: keyof Client, value: string | boolean) => {
    const previous = { ...client }
    const updated: Client = {
      ...client,
      [field]:
        field === 'tickers'
          ? parseList(String(value))
          : field === 'currencies'
            ? parseList(String(value))
            : value,
    }

    setClients((current) => current.map((item) => (item.id === client.id ? updated : item)))

    try {
      const payload: Record<string, unknown> = {}
      if (field === 'tickers') {
        payload.tickers = parseList(String(value))
      } else if (field === 'currencies') {
        payload.currencies = parseList(String(value))
      } else {
        payload[field] = value === '' ? null : value
      }

      const response = await fetch(`${API_BASE}/clients/${client.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error('Save failed.')
      }
      const data = await response.json()
      setClients((current) => current.map((item) => (item.id === client.id ? data : item)))
    } catch (err) {
      setClients((current) => current.map((item) => (item.id === client.id ? previous : item)))
      setError(err instanceof Error ? err.message : 'Save failed.')
    }
  }

  const handleClear = () => {
    const cleared = { q: '', ticker: '', currency: '' }
    setFilters(cleared)
    fetchClients(cleared)
  }

  const handleCreate = async () => {
    if (!createForm.client_name.trim()) {
      setError('Client name is required.')
      return
    }
    setError(null)
    try {
      const payload = {
        client_name: createForm.client_name.trim(),
        tickers: createForm.tickers ? parseList(createForm.tickers) : [],
        currencies: createForm.currencies ? parseList(createForm.currencies) : [],
        region: createForm.region.trim() || null,
      }
      const response = await fetch(`${API_BASE}/clients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error('Create failed.')
      }
      const data = await response.json()
      setClients((current) => [data, ...current])
      setCreateForm({ client_name: '', tickers: '', currencies: '', region: '' })
      setCreateOpen(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Create failed.')
    }
  }

  const handleDeleteSelected = async () => {
    if (!selectedClientId) return
    const confirmed = window.confirm('Delete this client? This cannot be undone.')
    if (!confirmed) return

    setError(null)
    try {
      const response = await fetch(`${API_BASE}/clients/${selectedClientId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Delete failed.')
      }
      setClients((current) => current.filter((item) => item.id !== selectedClientId))
      setSelectedClientId(null)
      setAuditItems([])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed.')
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Client Trading Preferences</p>
          <h1>Client Data Console</h1>
          <p className="subhead">
            Search by client name, filter by categories, and edit inline. No filters are saved to
            the database.
          </p>
        </div>
        <div className="status">
          {loading ? <span className="pill warning">Loading…</span> : <span className="pill">Live</span>}
          {error ? <span className="pill danger">{error}</span> : null}
        </div>
      </header>

      <section className="create-card">
        <div className="create-header">
          <div>
            <h2>Add Client</h2>
            <p>Create a new client row and start editing inline.</p>
          </div>
          <button className="primary" onClick={() => setCreateOpen((prev) => !prev)}>
            {createOpen ? 'Close' : 'New Client'}
          </button>
        </div>
        {createOpen ? (
          <div className="create-grid">
            <div className="field">
              <label htmlFor="new-client-name">Client Name</label>
              <input
                id="new-client-name"
                placeholder="Client name"
                value={createForm.client_name}
                onChange={(event) =>
                  setCreateForm((prev) => ({ ...prev, client_name: event.target.value }))
                }
              />
            </div>
            <div className="field">
              <label htmlFor="new-tickers">Tickers</label>
              <input
                id="new-tickers"
                placeholder="AAPL, NVDA"
                value={createForm.tickers}
                onChange={(event) =>
                  setCreateForm((prev) => ({ ...prev, tickers: event.target.value }))
                }
              />
            </div>
            <div className="field">
              <label htmlFor="new-currencies">Currencies</label>
              <input
                id="new-currencies"
                placeholder="USD, EUR"
                value={createForm.currencies}
                onChange={(event) =>
                  setCreateForm((prev) => ({ ...prev, currencies: event.target.value }))
                }
              />
            </div>
            <div className="field">
              <label htmlFor="new-region">Region</label>
              <input
                id="new-region"
                placeholder="Region"
                value={createForm.region}
                onChange={(event) =>
                  setCreateForm((prev) => ({ ...prev, region: event.target.value }))
                }
              />
            </div>
            <div className="actions">
              <button className="primary" onClick={handleCreate}>
                Save Client
              </button>
              <button
                className="ghost"
                onClick={() => {
                  setCreateForm({ client_name: '', tickers: '', currencies: '', region: '' })
                  setCreateOpen(false)
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : null}
      </section>

      <section className="chip-bar">
        <div className="chip-label">Active Filters</div>
        <div className="chips">
          {filters.q ? (
            <button
              className="chip"
              onClick={() => {
                const next = { ...filters, q: '' }
                setFilters(next)
                fetchClients(next)
              }}
            >
              Text: {filters.q}
            </button>
          ) : null}
          {filters.ticker ? (
            <button
              className="chip"
              onClick={() => {
                const next = { ...filters, ticker: '' }
                setFilters(next)
                fetchClients(next)
              }}
            >
              Ticker: {filters.ticker}
            </button>
          ) : null}
          {filters.currency ? (
            <button
              className="chip"
              onClick={() => {
                const next = { ...filters, currency: '' }
                setFilters(next)
                fetchClients(next)
              }}
            >
              Currency: {filters.currency}
            </button>
          ) : null}
          {!filters.q && !filters.ticker && !filters.currency ? (
            <span className="chip-empty">No filters applied</span>
          ) : null}
        </div>
      </section>

      <section className="filters">
        <div className="field">
          <label htmlFor="search">Search Client</label>
          <input
            id="search"
            placeholder="Search client name (e.g., RBIB)"
            value={filters.q}
            onChange={(event) => setFilters((prev) => ({ ...prev, q: event.target.value }))}
          />
        </div>
        <div className="field">
          <label htmlFor="ticker">Ticker</label>
          <div className="dropdown">
            <input
              id="ticker"
              placeholder="Filter by ticker(s) e.g. AAPL, NVDA"
              value={filters.ticker}
              onFocus={() => setTickerOpen(true)}
              onBlur={() => setTickerOpen(false)}
              onChange={(event) => setFilters((prev) => ({ ...prev, ticker: event.target.value }))}
            />
            {tickerOpen ? (
              <div className="dropdown-menu">
                {uniqueTickers.map((ticker) => (
                  <button
                    type="button"
                    key={ticker}
                    className="dropdown-item"
                    onMouseDown={(event) => {
                      event.preventDefault()
                      setFilters((prev) => ({
                        ...prev,
                        ticker: applyDropdownSelection(prev.ticker, ticker),
                      }))
                    }}
                  >
                    {ticker}
                  </button>
                ))}
                {uniqueTickers.length === 0 ? (
                  <div className="dropdown-empty">No tickers yet</div>
                ) : null}
              </div>
            ) : null}
          </div>
        </div>
        <div className="field">
          <label htmlFor="currency">Currency</label>
          <div className="dropdown">
            <input
              id="currency"
              placeholder="Filter by currency(s) e.g. USD, EUR"
              value={filters.currency}
              onFocus={() => setCurrencyOpen(true)}
              onBlur={() => setCurrencyOpen(false)}
              onChange={(event) =>
                setFilters((prev) => ({ ...prev, currency: event.target.value }))
              }
            />
            {currencyOpen ? (
              <div className="dropdown-menu">
                {uniqueCurrencies.map((currency) => (
                  <button
                    type="button"
                    key={currency}
                    className="dropdown-item"
                    onMouseDown={(event) => {
                      event.preventDefault()
                      setFilters((prev) => ({
                        ...prev,
                        currency: applyDropdownSelection(prev.currency, currency),
                      }))
                    }}
                  >
                    {currency}
                  </button>
                ))}
                {uniqueCurrencies.length === 0 ? (
                  <div className="dropdown-empty">No currencies yet</div>
                ) : null}
              </div>
            ) : null}
          </div>
        </div>
        <div className="actions">
          <button onClick={() => fetchClients()} className="primary">
            Apply Filters
          </button>
          <button onClick={handleClear} className="ghost">
            Clear Filters
          </button>
        </div>
      </section>

      <section className="table-card">
        <div className="table-meta">
          <span>{clients.length} clients</span>
          <span className="hint">Inline edits save immediately</span>
        </div>
        <div className="table-layout">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  {columnLabels.map((col) => (
                    <th key={col.key}>{col.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {clients.map((client) => (
                  <tr
                    key={client.id}
                    className={client.id === selectedClientId ? 'selected' : undefined}
                    onClick={() => {
                      setSelectedClientId(client.id)
                      fetchAudit(client.id)
                    }}
                  >
                    {columnLabels.map((col) => {
                      const value = client[col.key]
                      const isList = col.key === 'tickers' || col.key === 'currencies'
                      const displayValue = Array.isArray(value) ? formatList(value) : value ?? ''
                      const bufferKey = `${client.id}:${col.key}`
                      const bufferValue = editBuffer[bufferKey]
                      return (
                        <td key={`${client.id}-${col.key}`}>
                          {col.type === 'boolean' ? (
                            <input
                              type="checkbox"
                              checked={Boolean(value)}
                              onChange={(event) =>
                                updateClient(client, col.key, event.target.checked)
                              }
                            />
                          ) : (
                            <input
                              className="cell-input"
                              value={bufferValue ?? String(displayValue)}
                              placeholder={col.label}
                              onChange={(event) => {
                                const next = event.target.value
                                setEditBuffer((current) => ({ ...current, [bufferKey]: next }))
                              }}
                              onBlur={(event) => {
                                const nextValue = event.target.value
                                setEditBuffer((current) => {
                                  const copy = { ...current }
                                  delete copy[bufferKey]
                                  return copy
                                })
                                updateClient(client, col.key, isList ? nextValue : nextValue)
                              }}
                              onKeyDown={(event) => {
                                if (event.key === 'Enter') {
                                  event.currentTarget.blur()
                                }
                              }}
                              onClick={(event) => event.stopPropagation()}
                            />
                          )}
                        </td>
                      )
                    })}
                  </tr>
                ))}
                {!loading && clients.length === 0 ? (
                  <tr>
                    <td colSpan={columnLabels.length} className="empty">
                      No results. Try clearing filters or loading the seed data.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
          <aside className="audit-panel">
            <div className="audit-header">
              <h2>Audit History</h2>
              <div className="audit-actions">
                {selectedClientId ? <span className="pill">Client selected</span> : null}
                {selectedClientId ? (
                  <button type="button" className="danger-btn" onClick={handleDeleteSelected}>
                    Delete Client
                  </button>
                ) : (
                  <span className="pill warning">No client selected</span>
                )}
              </div>
            </div>
            {auditLoading ? (
              <p className="audit-muted">Loading audit history…</p>
            ) : selectedClientId ? (
              auditItems.length > 0 ? (
                <ul className="audit-list">
                  {auditItems.map((item) => (
                    <li key={item.id}>
                      <div className="audit-row">
                        <span className="audit-field">{item.field_name}</span>
                        <span className="audit-time">
                          {new Date(item.changed_at).toLocaleString()}
                        </span>
                      </div>
                      <div className="audit-values">
                        <span className="audit-old">{item.old_value ?? '—'}</span>
                        <span className="audit-arrow">→</span>
                        <span className="audit-new">{item.new_value ?? '—'}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="audit-muted">No changes recorded yet.</p>
              )
            ) : (
              <p className="audit-muted">Select a client row to view changes.</p>
            )}
          </aside>
        </div>
      </section>
    </div>
  )
}

export default App
