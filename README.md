# veoveo-template-installation

A Veoveo installation records its identity provider, permissions, component revisions
and environment compositions. Lore owns source; OpenShell executes factory and MCP
workloads through its native Docker driver.

The old `autonomy` and `runtime` launchers have been removed. `compose.yaml` contains
trusted bootstrap only: Lore, local identity, PostgreSQL, SeaweedFS and the required
Lore Desktop authentication/TLS integration. Their named data volumes are external
and survive bootstrap removal. OpenShell runs as the native macOS gateway service.

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
pinned Rust toolchain for OpenShell. The Lore server remains upstream. DeepInfra
model settings are present; this first Lore-only factory has no inference provider
attached and makes no model requests.

Native workload definitions, provider profiles and operator setup live under
`openshell/`. Use the same runtime interface for authoring, checks and deployed MCP
services. Source revisions and runtime image digests identify the deployed version.

## Lore Desktop

The existing remote remains `grpcs://localhost:7443`. The Desktop edge forwards
user credentials to upstream Lore, and `veoveo-service-lore` adapts its published
Desktop authentication/catalog protocol to the configured OIDC provider. This is
required protocol adaptation. Local Keycloak is permanent; external installations
provide their own OIDC issuer/client settings.

The old runtime was removed on macOS. The native Lore and private MCP path has focused acceptance; exact operating
commands are in [OpenShell setup](openshell/README.md). Compatible infrastructure
migration and full application composition remain subsequent work. See [the hard-cut record](../veoveo-docs/OPENSHELL_HARDCUT_PLAN.md).
