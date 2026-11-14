# Zero-Token AI Voice Receptionist
Local-first, multi-tenant AI receptionist platform using Ollama, pgvector, and local speech tooling. Hosted LLM token charges are avoided; infrastructure, telephony, compute, and energy still cost money.

## Current implementation
- Tenant signup + administrator account; email/password login; 12-hour signed JWT.
- API tenant membership checks on business/call/knowledge/reply routes.
- Tenant-filtered pgvector retrieval and locally hosted Ollama inference.
- Local transcription adapter and industry prompt starter packs.
- Docker Compose development stack and initial SQL schema.

## Quick start
See [docs/QUICKSTART.md](docs/QUICKSTART.md). Use a strong `APP_SECRET`; never deploy the current MVP directly to the public internet.

## API auth
- `POST /v1/auth/signup`: business_name, slug, industry, email, password (12+ chars)
- `POST /v1/auth/login`: email/password -> bearer token
- `GET /v1/auth/me`: authenticated account
- Business endpoints require `Authorization: Bearer <access_token>` and matching tenant ID.
Swagger UI: `/docs`.

## Honest status
This is a development MVP, not a production-ready phone system. SIP/PSTN integration, real-time WebRTC media, streaming TTS/barge-in, billing, robust dashboard, Alembic migrations, email verification/password reset/MFA, rate limits, audit/retention controls, and comprehensive tests remain. See [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/SECURITY.md](docs/SECURITY.md).
