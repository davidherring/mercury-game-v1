# Mercury Frontend (Vite + React + TS)

## Setup
```bash
cd frontend
npm install
npm run dev
```

- Backend must be running locally on `http://127.0.0.1:8000`.
- Default API base is `/api` (proxied to the backend in `vite.config.ts`).
- You can override the base URL in the UI header; it is stored in `localStorage`. Env override: `VITE_API_BASE_URL`.

## Notes
- Uses fetch (no axios) and a small API client in `src/api/client.ts`.
- No routing yet; the layout renders placeholder panels for upcoming flows.
