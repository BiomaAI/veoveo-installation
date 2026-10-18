# Agent Instructions

- This repository holds Bioma's real installation choices and trusted bootstrap
  configuration, based on `VeoveoAI/veoveo-template-installation`. Send reusable
  fixes upstream; keep Bioma-specific native selections in `openshell/bioma/`.
  Planning and acceptance evidence belong in `VeoveoAI/veoveo-docs`. Components
  own their build and check logic. Update this repository when its actual deployed
  configuration or qualification status changes.
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
  Preserve ordinary Lore operations and upstream security boundaries. The factory
  branch guard belongs in Lore's existing pre-push hook and trusted configuration;
  it is not a comprehensive branch authorization or transport-expiry system.
  Credential lifecycle qualification stays separate in native OpenShell controls.
- The user withdrew Desktop acceptance on 2026-10-17. Follow
  [the direct Lore credential plan](https://github.com/VeoveoAI/veoveo-docs/blob/main/LORE_DIRECT_OIDC_PLAN.md): IdP
  issuance, native OpenShell renewal/injection and native Lore resource grants.
  The Desktop adapter, signer and ingress are retired. Do not restore them or add
  a machine-token endpoint, new signer or refresh daemon. Historical Desktop results
  are not active operator instructions or completion gates.
- Never commit credentials. `.env`, TLS/private state and local backups remain
  ignored and excluded from build contexts. Protect durable data independently of
  disposable sandbox lifecycle.
- Use upstream bootstrap images pinned by digest. Verify releases when changing pins.
  Generic examples use `https://veoveo.example.com`. Bioma's selected native files
  may use its actual public domains and public application IDs; credentials,
  operator principal grants and generated private state stay ignored.
- Validate changed bootstrap configuration and the focused new path on macOS.
  The reference Linux deployment, Entra and signed Media webhook are now in scope
  under the execution plan. Preserve remote state; GPU/CUDA qualification is separate.
- Commit coherent changes without AI attribution.
