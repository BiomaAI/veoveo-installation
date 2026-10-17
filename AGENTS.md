# Agent Instructions

- This repository holds installation choices and trusted bootstrap configuration.
  Planning belongs in `veoveo-docs`. Components own their build and check logic.
- All coding factories and managed MCP workloads use OpenShell's native Docker
  driver. Use its existing APIs, lifecycle, credential store, policy and diagnostics.
  Do not add Compose author/application profiles, a token worker or a second launcher.
- Use permanent Keycloak locally and provider-agnostic OIDC configuration elsewhere.
  Generic installation must not require Keycloak administration credentials.
- Real provider tokens, signing keys, operator state, bootstrap volumes and Docker
  access stay outside author and agent-controlled service workloads. Use native
  OpenShell credential mediation. Unsupported enforcement fails closed.
- Prefer upstream configuration and extension points. Maintained, revision-pinned
  VeoveoAI security/transport patches are allowed by the accepted architecture.
  Preserve ordinary Lore operations and upstream security boundaries.
- Never commit credentials. `.env`, TLS/private state and local backups remain
  ignored and excluded from build contexts. Protect durable data independently of
  disposable sandbox lifecycle.
- Use upstream bootstrap images pinned by digest. Verify releases when changing pins.
  Committed public origins use `https://veoveo.example.com`.
- Validate changed bootstrap configuration and the focused new path on macOS.
  The existing Linux installation is out of scope for this cutover.
- Commit coherent changes without AI attribution.
