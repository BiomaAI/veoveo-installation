# Agent Instructions

- This repository holds Bioma's real installation choices and trusted bootstrap
  configuration, based on `VeoveoAI/veoveo-template-installation`. Send reusable
  fixes upstream; keep Bioma-specific native selections in `openshell/bioma/`.
  Planning and acceptance evidence belong in `VeoveoAI/veoveo-docs`. Components
  own their build and check logic. Update this repository when its actual deployed
  configuration or qualification status changes.
- Linux deployment uses K3s foundation controllers and OpenShell's native Kubernetes
  driver for Hub/MCP, Computer and factory workloads. Mac development/test fixtures
  remain in the generic template, not this Linux launch path. Use native APIs,
  lifecycle, credential store, policy and diagnostics. Do not add an orchestrator,
  Helm sandbox inventory, token worker or second launcher.
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
- Entra authenticates humans. Hub's existing issuer and live revisioned control
  plane own explicit repository assignments/native Lore tokens; native Lore enforces
  its unchanged token/permission contract. OpenShell renews/injects factory grants;
  human Lore refresh remains private to each Computer. Do not restore the withdrawn
  direct-IdP grant helper, Desktop adapter, signer or ingress, or add a token worker,
  custom Lore rules, implicit admin/member repository rights or global grants.
- Never commit credentials. `.env`, TLS/private state and local backups remain
  ignored and excluded from build contexts.
- During rapid development, application data is disposable for authorized resets
  on breaking contracts; do not add migrations, backward compatibility or backups
  merely to retain development data. Retain source and trusted installation/identity
  configuration as rebuild inputs. Preserve normal durable ownership across routine
  sandbox lifecycle; revisit retention when production data enters scope.
- Use upstream bootstrap images pinned by digest. Verify releases when changing pins.
  Generic examples use `https://veoveo.example.com`. Bioma's selected native files
  may use its actual public domains and public application IDs; credentials,
  operator principal grants and generated private state stay ignored.
- Validate changed bootstrap configuration and the focused new path on macOS.
  The reference Linux deployment, Entra and signed Media webhook are now in scope
  under the execution plan. GPU/CUDA qualification is separate.
- Commit coherent changes without AI attribution.
