# Security baseline (v0.3)
## Identity and tenant boundaries
- Self-service signup creates one business tenant and its first administrator.
- Email/password login issues an HS256 bearer token valid for 12 hours.
- Tenant API routes enforce authenticated user's tenant UUID; clients cannot select another tenant.
- Platform tenant creation is reserved for a `platform_admin` role.
- Passwords use PBKDF2-HMAC-SHA256 (310,000 iterations) and random per-password salts.
- WebSocket text sessions require a signed token in the `token` query parameter and matching tenant claim.
## Before internet/public production
1. Set a high-entropy `APP_SECRET` (32+ random bytes); rotate/manage with a secret manager.
2. Add HTTPS/WSS, rate limits on signup/login/inference.
3. Add email verification, password reset, MFA, audit events, and administrator invite/role workflows.
4. Configure backups, Alembic migrations, retention/deletion, and incident response.
5. Avoid bearer tokens in URL logs; WebSocket query-token transport is temporary. Prefer short-lived ticket exchange.
6. Apply call recording consent/notice, local legal requirements, and explicit data retention policies.
7. Run security review, dependency scanning, automated tests, and tenant-isolation tests.
This is an MVP security improvement, not production certification.
