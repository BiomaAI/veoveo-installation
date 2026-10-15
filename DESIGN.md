# Local Installation

This template's defaults run a whole Veoveo installation on one workstation with
Docker Compose: the infrastructure, an Envoy edge, a Lore server and one environment per
component. The `runtime` containers hold trusted component state and approved source snapshots;
coding agents run only in the separate `autonomy` profile described below. The design
follows decisions D40 to D43 of the
[repository split plan](https://github.com/VeoveoAI/veoveo-docs/blob/main/REPOSITORY_SPLIT_PLAN.md#decisions);
[README.md](README.md) holds the commands.

## Standards And Protocols

| Standard or protocol | Use |
|---|---|
| Compose specification, Docker Compose 2.24 or newer | Services, the `runtime`, `autonomy` and `tunnel` profiles, internal networks with fixed subnets, named volumes and `additional_contexts` for the environment layer |
| Dockerfile syntax 1.27 with BuildKit | The environment layer over each component's `dev` image, and the Lore build, which fetches its source with `ADD` of a Git URL at one commit |
| Envoy 1.40.0, v3 static bootstrap | The edge: TCP proxies for published ports, HTTP connection managers, RBAC on the source address, the generic credential injector reading SDS file secrets, `ExtensionWithMatcher` with `SkipFilter`, and the dynamic forward proxy |
| HTTP CONNECT, RFC 9110 §9.3.6 | The edge's egress proxy at `vv-egress.internal:3128`, which opens tunnels only to allowlisted hosts on port 443 |
| TLS 1.3 with X.509 certificates, RFC 5280 | The installation CA, an ECDSA P-256 key, and the certificates it signs for `vv-lore.internal` and `media-provider.internal`; every environment trusts the CA through its system store |
| `.internal`, the top-level domain ICANN reserves for private networks | Every container's network name, where core's [conventions](https://github.com/VeoveoAI/veoveo-core/blob/main/docs/CONVENTIONS.md#http-paths) allow plain HTTP |
| Unmodified Lore v0.10.1 from [EpicGames/lore](https://github.com/EpicGames/lore) at `95a9a834` | Both client and server are upstream source. Clients use `grpcs://` through Envoy for revisions and storage; QUIC is disabled |
| OAuth 2.0 client credentials, RFC 6749 §4.4, with RFC 7523 assertions and RFC 8707 resources | How the Lore token service obtains each environment's token from the Gateway |
| JWT access tokens, RFC 9068 | Lore tokens with the `lore_resources` claim, profiled in the Gateway's [Lore tokens](https://github.com/VeoveoAI/veoveo-service-gateway/blob/main/crates/veoveo-service-gateway/DESIGN.md#lore-tokens) |
| [Component lock](https://github.com/VeoveoAI/veoveo-core/blob/main/platform/installation/contract/DESIGN.md), `https://veoveo.ai/formats/component-lock` | `component-lock.json`, the revision of each component the installation builds and snapshots into Lore |

## Services

| Service | Image | Networks | Purpose |
|---|---|---|---|
| `vv-postgres` | PostgreSQL 18.6 by digest | `vv-local`, `vv-outside` | The installation database |
| `vv-seaweedfs` | SeaweedFS 4.48 by digest | `vv-local`, `vv-outside` | The object store |
| `vv-egress` | Envoy 1.40.0 by digest | `vv-local`, `vv-media`, `vv-outside` | The edge |
| `vv-lore` | built from `lore/Dockerfile` | `vv-local` | The Lore server, storing on its volume |
| `vv-autonomy-tokens` | the pinned Gateway refresher image | `vv-local` | Refreshes Envoy SDS credentials in trusted storage |
| `vv-review` | the upstream Lore image | `vv-review` | Repository administration through the isolated Envoy admin listener; never executes repository code |
| `vv-srv-gateway`, `vv-mcp-time`, `vv-mcp-artifact`, `vv-mcp-media` | the environment layer over each component's `dev` image | `vv-local`, and `vv-media` for Media | The environments |
| `vv-tunnel` | cloudflared 2026.10.0 by digest | host | The public origin's tunnel, optional |

PostgreSQL, SeaweedFS and the edge start by default. The `runtime` profile adds trusted component containers. The `autonomy` profile adds
Lore, the SDS refresher, Envoy, the reviewer and development containers. Lore and token
issuance need the Gateway to be running first.

## Environments

The runtime layer, `runtime/Dockerfile`, adds the installation CA to each component's
`dev` image and strips all setuid/setgid bits. It installs no Lore client or token
loader. Runtime containers run as `sandbox`, with all capabilities dropped and
`no-new-privileges` enabled. Their named `/sandbox` volumes retain trusted component
state and approved source snapshots. They never run coding agents.

A runtime compiles its approved snapshot at `/sandbox/src`. The served binary builds
into `/sandbox/target-serve`, apart from test builds. Recreating the container preserves
its volume, but component processes launched through `docker exec` must be restarted.
Lore operations run only in the separate development and review containers. Deployment
exports an approved snapshot through the reviewer; no runtime needs a Lore credential.

## Networks And Names

`vv-local`, `10.231.10.0/24`, is an internal network that no route leaves. The
environments, Lore, PostgreSQL and SeaweedFS share it, and each answers under its
`.internal` name, such as `vv-mcp-time.internal`. `vv-media`, `10.231.11.0/24`, is also
internal and holds only Media's environment and the edge. `vv-outside` is an ordinary
bridge network for the edge and the infrastructure's published ports.

A runtime reaches PostgreSQL, the object store and the other runtime services
directly on `vv-local`. It reaches the Gateway at `vv-gateway.internal`, which is the
edge, and everything else only through the edge's proxy. `NO_PROXY` keeps every
`.internal` name off the proxy, so signed object-store requests reach SeaweedFS
unchanged.

## Edge

The edge's configuration is `egress/envoy.yaml`. `egress/render` writes the copy Envoy
reads, filling in the hosts `.env` names: the public origin's, the media provider API's
and the provider's output hosts.

| Listener | Admits | Does |
|---|---|---|
| `vv-gateway.internal:8080` | `vv-local` | Forwards to the Gateway and replaces `Authorization` with the registration secret on `POST /oauth/register` only, so registration access tokens on `/oauth/register/{client}` pass unchanged |
| `media-provider.internal:443` | `vv-media` | Terminates TLS with the installation CA's certificate, replaces `Authorization` with the provider's key, and forwards to the provider's API over TLS verified against public roots |
| `vv-egress.internal:3128` | `vv-local`, `vv-media` | Opens CONNECT tunnels to `static.rust-lang.org`, `index.crates.io`, `static.crates.io`, `crates.io`, `github.com`, `api.github.com` and the rendered hosts, and answers 403 to every other host |
| `127.0.0.1:8080`, `8800`, `8801`, `8802` on the host | the host and the tunnel | Forward to the Gateway and the servers without adding any secret |

The registration secret and the provider key live in the `vv-egress-secrets` volume,
which only the edge mounts. A matcher wraps the registration injector because Envoy's
credential injector takes no per-route configuration. Environments hold placeholders,
so a request that bypasses the edge carries no secret.

## Lore

Each component has one Lore repository, created by the Lore admin from a snapshot of the
component's locked GitHub revision: `git archive` of that commit, committed as one Lore
revision on `main`, which the admin then protects. A component update is a new snapshot
commit on `main`. Nothing in Lore returns to GitHub. An environment pushes its own
branches; Lore refuses its pushes to the protected `main`, and the admin, a service
account, merges.

The Gateway issues Lore tokens. `generate-local-installation` creates clients and
signing keys for each component and the reviewer in trusted Gateway state. Repository
grants give each development client access to its own repository. The SDS refresher
publishes those credentials to Envoy; no Lore client has a credential file.

The Lore server reads the Gateway's keys at startup, so the Gateway starts first from
its locked GitHub snapshot. Runtime source stays a trusted snapshot. `vv-review`
creates repositories from host-exported snapshots and administers protected branches.

## Coding Agents

The `autonomy` profile separates source/build/test state from trusted runtime state.
`vv-dev-*` never mounts a runtime volume, token file, host directory or Docker socket.
Each runs as UID 1000, with every capability dropped and `no-new-privileges`, on a
separate internal /29 network. The new environment layer strips all setuid/setgid
bits. Runtime containers keep private service state and have no Lore tooling; they
are never agent environments, including the Gateway container holding signing keys.

`vv-autonomy-edge` is an unmodified, digest-pinned Envoy. It joins the four development
networks, a separate trusted review network, the backend and the outside network.
Each Lore listener binds only its own network address and admits its single dev peer
using `direct_remote_ip`. It injects that component's token regardless of supplied
headers. The reviewer gets a separate admin route. Devs cannot reach the backend,
other dev networks, the reviewer route or Envoy's loopback admin interface.

Lore's existing `grpcs://` transport covers both storage and revisions. Envoy terminates
TLS at `lore-proxy.internal:7443` and verifies `vv-lore.internal` over HTTP/2 TLS.
Repository grants and protected branches are still enforced by the unchanged Lore
server. No Lore repository operation, merge, revision or storage logic changes.
The installation carries no Lore source patches, privileged token loader, or direct
client authentication fallback. The upstream server disables QUIC because all client
operations use the authenticated gRPC route.

`autonomy/component-lock.json` pins the Gateway revision for the trusted refresher
without changing the deployed component snapshots. Its `lore-tokens`
command publishes each named generic secret
as a complete filesystem SDS response, with a synced file and atomic rename. The
trusted refresher owns the signing keys and mounts its output volume read-write;
only Envoy mounts it read-only. Fifteen-minute tokens refresh every ten minutes.
The refresher emits SDS responses only; raw-token compatibility has been removed.

`inference.internal:8443` accepts only POST `/v1/chat/completions` and forwards to
`api.deepinfra.com/v1/openai/chat/completions` with verified TLS and replaced
authorization. Its sole key lives in an edge-only volume. Streaming responses and tool-call continuations use
the same fixed route. Dependency CONNECT tunnels allow only explicit public
Rust/crates.io/GitHub destinations. There is no general authenticated forward proxy.

OpenCode v2.0.29 is pinned by npm integrity for both CPU architectures. Root-owned
managed configuration selects MiMo V2.6 Pro through DeepInfra, disables
updates and Git snapshots, and supplies only a placeholder credential. Lore provides
checkpoints. OpenCode policy is guidance and configuration control; isolation does
not depend on the model following instructions. Shell code still has only the dev
container's filesystem, processes and network capabilities.

Source acceptance and runtime promotion are separate. The reviewer inspects and tests
agent work before merging a Lore task branch. No agent output automatically executes
in a service holding keys. Runtime deployment remains an explicit trusted action.

## Qualification

On October 14 on macOS, a reset from the README brought the installation up from
nothing. Time passed 6 acceptance tests, Artifact 7, its gibibyte upload and share route
included, and Media 2 with the fake provider; all passed again after every environment
was recreated. Each environment cloned its own repository and got "Not found" for
another. A push to protected `main` was refused, and a branch push and the admin's merge
succeeded. No environment's readable files, variables or `lore -d` output held its Lore
token or the registration secret, apart from the Gateway's own state. The egress proxy
reached crates.io and GitHub and refused other hosts, and a Lore clone succeeded after
the first token had expired.

On October 15, the `autonomy` profile was qualified on Docker Desktop on macOS.
All four dev containers cloned their own repository with `NoNewPrivs: 1`, no token
files and no privileged executables. Cross-repository access failed. A forged admin
JWT was overwritten: the same client could clone its own repository but could not
clone another. A real update to a protected disposable branch was refused even with
an admin author identity; the probe branch was then archived. Network probes refused
other dev routes, the review route, backend services, direct internet access, the
Envoy admin interface, unlisted CONNECT destinations and spoofed inference hosts/paths.
All dev containers were recreated and retained their workspaces and OpenCode state.
Lore-specific ignore rules were then checked by staging a disposable clone: root and
nested `.env` files and build output stayed excluded, while the three env template
forms remained stageable. Git exclusions alone do not apply to Lore.

Envoy accepted filesystem SDS rotation with zero rejected updates. After the original
15-minute credential expired, a fresh Time clone and repository integrity verification
succeeded. The Gateway's complete Docker check gate passed all 199 tests. Time's stale
local branch pointer was repaired with the existing reset/sync commands after backup;
its original checkout now reports main synchronized and passes repository verification.

OpenCode 2.0.29 and MiMo completed a streamed model/tool round trip that ran Lore status.
A longer session created `agent/get-clock-20261015` and inspected the Time source, but
Hugging Face returned HTTP 402 (no remaining inference credits) before code edits.
The user subsequently replaced the coding exercise with a command-only smoke test
and selected DeepInfra. The original session remains as an audit log; the unused task branch was archived
during cleanup. No agent-produced code has been deployed or accepted into main. DeepInfra connectivity
through Envoy passed with a 16-token request. A fresh OpenCode session then made
exactly one shell call, `lore -P --repository /sandbox/src status`, which exited zero
under `no-new-privileges`. Two model steps used 100 output tokens and no reasoning
tokens. The command reported the existing local task branch at revision 9 with no
remote branch; it made no source edits. Separate Linux-host gates remain required
before publishing changes.

On October 15 the installation switched both Lore binaries to the unmodified
upstream v0.10.1 release commit. A fresh Time clone and repository integrity check
passed through Envoy. A committed text fixture pushed to a task branch and cloned
correctly in the reviewer. After the reviewer protected that branch, another changed
push was denied even with a claimed admin identity. A forged credential was replaced
for the authorized repository and did not grant access to another repository. Main
remained at revision 9. The test branches and earlier empty task branches were archived.

All four runtime containers were rebuilt without Lore, token mounts or privileged
helpers and restarted with `no-new-privileges`. Their existing service state and five
running processes were preserved. The old admin and raw-token refresher containers,
the old admin image, and their six obsolete volumes were removed after backing up the
admin workspace. The Gateway's SDS-only refresher passed its full Docker check gate:
199 tests, formatting, linting and dependency/feature checks. No inference call or
coding-agent session was needed for this migration.

## Gaps

- The real media provider through `media-provider.internal` is configured and was not
  qualified with a billed run; the egress tests qualified the route with a stand-in.
- The Linux host has not run this installation, and GPU environments wait for the GPU
  components.
- Runtime services hold private state and must never run agents.
- Lore's gRPC verifies the server against the installation CA by name; the
  client does not pin the server's certificate.
