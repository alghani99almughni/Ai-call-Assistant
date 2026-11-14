# Roadmap / implementation status

## In this branch (starter)
- [x] FastAPI health and text-turn endpoint
- [x] WebSocket text-turn scaffold
- [x] Local Ollama adapter
- [x] Local faster-whisper transcription helper
- [x] multilingual-e5 embedding helper (384 dimensions)
- [x] initial pgvector schema, tenant keys on data tables
- [x] starter industry prompt packs
- [x] Compose services (Postgres/pgvector, Redis, Ollama, API)

## Not production complete
- [ ] Audio/WebRTC/SIP media pipeline and streaming ASR/TTS (Pipecat, SIP provider)
- [ ] Kokoro streaming speech output and barge-in
- [ ] tenant-safe database repositories + RLS policies
- [ ] authentication, password hashing, sessions/JWT, RBAC middleware
- [ ] knowledge upload parsing, chunking, embedding persistence and retrieval query
- [ ] Redis rolling conversation context and durable transcript writes
- [ ] tool/function execution with allowlisted schemas and audit records
- [ ] tenant onboarding and CRUD APIs
- [ ] Next.js customer/admin portals, embed widget, usage and analytics
- [ ] call recording consent, retention, deletion, PII redaction
- [ ] migrations, automated tests, CI, observability, rate limits and security review

No per-token model API fees does not mean zero operating cost: compute, power, telecom/SIP,
hosting, storage, and maintenance remain.
