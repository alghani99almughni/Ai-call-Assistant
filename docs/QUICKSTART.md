# Local quickstart

1. Install Docker Desktop (or Docker Engine + Compose).
2. Copy `.env.example` to `.env`; replace all development credentials.
3. Run `docker compose up --build -d`.
4. Pull the model once: `docker compose exec ollama ollama pull qwen2.5:7b`.
5. Open portal at http://localhost:3000 and API docs at http://localhost:8000/docs.
6. Create tenant via POST /v1/tenants. Copy the returned UUID.
7. Create a call session via POST /v1/tenants/{tenant_id}/calls.
8. Add knowledge via POST /v1/tenants/{tenant_id}/knowledge (JSON source_name/content).
9. Post a question to POST /v1/tenants/{tenant_id}/calls/{call_id}/reply.

## Hardware notes
Qwen 7B and Whisper are resource-intensive. CPU mode works slowly; GPU acceleration needs a compatible host/runtime setup. Local inference means no token-metered hosted model API, not zero electricity/compute or phone costs.

## Security warning
This prototype has no authentication middleware yet. Tenant UUIDs are not credentials. Do not deploy to a public internet or put real customer data in it. Implement identity, membership checks, rate limiting, consent, encryption, and retention controls first.
