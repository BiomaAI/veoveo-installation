# veoveo-template-installation

A Veoveo installation records approved identity, component revisions and environment
configuration. Lore owns source/revisions; native OpenShell executes factories and
managed MCP workloads through its Docker driver.

Factory credentials follow one path: **IdP issuance → native OpenShell renewal and
injection → native Lore authorization**. Veoveo supplies trusted configuration and
branch assignments. There is no Veoveo token service, refresh daemon or signer.
The existing small pre-push hook guards normal factory pushes; native branch
protection remains effective. It is not complete isolation against storage APIs.

## Local bootstrap

Keep the ignored `.env`, installation CA and private operator state. Local Keycloak
and its dedicated PostgreSQL are permanent bootstrap, alongside Lore, PostgreSQL,
SeaweedFS and the Keycloak HTTPS ingress. Their external data volumes survive
Compose cleanup. The native OpenShell gateway runs as the macOS service.

Complete the one-time [CA trust setup](identity/README.md#macos-certificate-trust),
then follow [native OpenShell setup](openshell/README.md). Existing installations
provision approved Lore identities with `./identity/configure-lore` and use
`docker compose --profile keycloak up -d`. The former OIDC egress proxy is retired;
workload egress follows native OpenShell policy and credential mediation.
A fresh installation must first provision identity credentials and external volumes.
No agent joins bootstrap networks, mounts operator state or accesses Docker.

`factory/` packages OpenCode 2.0.29, the existing Lore CLI auth fixes and a pinned
Rust toolchain. The server uses native OIDC with its public CA trust and the
existing hook extension. The first smoke factory's RPC policy is read-only and
has no inference provider. Build commands select the required patched sources;
the [execution checklist](../veoveo-docs/OPENSHELL_HARDCUT_PLAN.md) records current acceptance.

For the Entra-backed reference Linux goal, follow the existing native contracts
and [reference preparation](openshell/REFERENCE.md). It uses no local Keycloak
stack and introduces no alternate application launcher.

## Scope and recovery

Desktop acceptance was withdrawn. Its adapter, signing/manual-token helpers and
Desktop-only ingress are retired; `grpcs://localhost:7443` is no longer an active
endpoint. Private signing/session recovery state and durable Lore/identity data
are preserved.

The local direct-issuer path has focused qualification. The reference Linux/Entra
and signed webhook goal is active in the
[execution plan](../veoveo-docs/OPENSHELL_HARDCUT_PLAN.md). Customer issuers,
interactive human Lore login, GPU/CUDA and general environment composition remain
separate qualifications.
