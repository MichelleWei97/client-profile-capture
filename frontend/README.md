# Frontend (React + TypeScript)

This is the UI for the client data table with inline editing and filters.

## Suggested setup (Vite)
1. Create the React app
   - `npm create vite@latest . -- --template react-ts`
2. Install dependencies
   - `npm install`
3. Start dev server
   - `npm run dev`

## UI requirements
- Data table with 15 columns
- Inline editing on cells
- Filters (categories + text search)
- Clear filters resets to full dataset
- Save updates to backend via `PATCH /clients/:id`
- Optional audit history view
