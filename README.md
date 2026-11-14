# Zero-Token Voice Receptionist

Local-first, multi-tenant AI receptionist starter. Inference runs on your own hardware (Ollama, faster-whisper, Kokoro); there are no per-token API fees. Hardware, telephony, hosting, and bandwidth still cost money.

## MVP architecture
- FastAPI API + WebSocket text-turn endpoint
- PostgreSQL + pgvector schema for tenant-isolated knowledge
- Redis for short-lived conversation state
- Ollama chat completion (local)
- faster-whisper transcription (local)
- Docker Compose for development

## Quick start
1. Copy `.env.example` to `.env` and set strong secrets.
2. `docker compose up --build`
3. API docs: http://localhost:8000/docs

The starter is intentionally honest about integrations: SIP/WebRTC media, production identity, tenant provisioning, and deployment hardening are follow-up work. Do not expose publicly before implementing those controls.

## Branch
Implementation: `zero-token-voice-receptionist`
