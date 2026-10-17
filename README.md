# veoveo-template-installation

A Veoveo installation records its identity provider, permissions, component revisions
and environment compositions. Lore owns source; OpenShell executes factory and MCP
workloads through its native Docker driver.

The old `autonomy` and `runtime` launchers have been removed. `compose.yaml` contains
trusted bootstrap only: Lore, local identity, PostgreSQL, SeaweedFS and the existing
Lore Desktop authentication/TLS integration. Their named data volumes are external
and survive bootstrap removal. OpenShell runs as the native macOS gateway service.

Desktop acceptance was withdrawn on 2026-10-17. The next implementation uses
[direct IdP-issued Lore credentials and native OpenShell renewal](../veoveo-docs/LORE_DIRECT_OIDC_PLAN.md),
then retires the Desktop adapter and ingress. The bootstrap commands below describe
the still-deployed configuration until that cutover is qualified.

## Local bootstrap

Keep the ignored `.env`, installation CA and existing operator state. For an existing
installation, run `./egress/render` and `docker compose --profile keycloak --profile
desktop up -d`. A fresh installation must provision the identity credentials and the
external data volumes first. See [identity](identity/README.md) and [the infrastructure
plan](../veoveo-docs/INFRASTRUCTURE_CANDIDATE.md).

On macOS, complete the one-time [installation CA trust setup](identity/README.md#macos-certificate-trust)
in the user's login keychain before OpenShell login. This is an installation step;
ordinary CLI use needs no certificate environment exports. Then follow the
[native OpenShell commands](openshell/README.md#operator-state-and-identity).

`vv-egress` permits only configured OIDC hosts for trusted bootstrap authentication.
OpenShell owns factory/model/API credential mediation. No agent joins bootstrap
networks or mounts their state.

## Factories and services

`factory/` packages OpenCode v2, the Lore CLI with narrow auth-only patches, and a
pinned Rust toolchain for OpenShell. The Lore server is an extension build with a
small existing pre-push hook for trusted factory assignments. Ordinary Lore
repository authorization, storage, branch protection and transport are unchanged. DeepInfra
model settings are present; this first Lore-only factory has no inference provider
attached and makes no model requests.

Native workload definitions, provider profiles and operator setup live under
`openshell/`. Use the same runtime interface for authoring, checks and deployed MCP
services. Source revisions and runtime image digests identify the deployed version.

## Lore Desktop (pending retirement)

The existing remote remains `grpcs://localhost:7443`. The Desktop edge forwards
user credentials to upstream Lore, and `veoveo-service-lore` adapts its published
Desktop authentication/catalog protocol to the configured OIDC provider. That
adaptation serves the withdrawn Desktop requirement; it is not a required factory
service. Do not extend it with token issuance for OpenShell. Local Keycloak stays;
the direct replacement uses native Lore resource grants and OpenShell providers.

The old runtime was removed on macOS. The native Lore and private MCP path has focused acceptance; exact operating
commands are in [OpenShell setup](openshell/README.md). Compatible infrastructure
migration and full application composition remain subsequent work. See [the hard-cut record](../veoveo-docs/OPENSHELL_HARDCUT_PLAN.md).
