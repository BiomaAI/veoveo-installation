# Local Installation

This template's defaults run a whole Veoveo installation on one workstation with
Docker Compose: the infrastructure, an Envoy edge, a Lore server and one environment per
component. An environment is the container where a component's source lives, builds,
runs and passes its acceptance tests, and where a coding agent works on it. The design
follows decisions D40 to D43 of the
[repository split plan](https://github.com/VeoveoAI/veoveo-docs/blob/main/REPOSITORY_SPLIT_PLAN.md#decisions);
[README.md](README.md) holds the commands.

## Standards And Protocols

| Standard or protocol | Use |
|---|---|
| Compose specification, Docker Compose 2.24 or newer | Services, the `envs` and `tunnel` profiles, internal networks with fixed subnets, named volumes and `additional_contexts` for the environment layer |
| Dockerfile syntax 1.27 with BuildKit | The environment layer over each component's `dev` image, and the Lore build, which fetches its source with `ADD` of a Git URL at one commit |
| Envoy 1.40.0, v3 static bootstrap | The edge: TCP proxies for published ports, HTTP connection managers, RBAC on the source address, the generic credential injector reading SDS file secrets, `ExtensionWithMatcher` with `SkipFilter`, and the dynamic forward proxy |
| HTTP CONNECT, RFC 9110 §9.3.6 | The edge's egress proxy at `vv-egress.internal:3128`, which opens tunnels only to allowlisted hosts on port 443 |
| TLS 1.3 with X.509 certificates, RFC 5280 | The installation CA, an ECDSA P-256 key, and the certificates it signs for `vv-lore.internal` and `media-provider.internal`; every environment trusts the CA through its system store |
| `.internal`, the top-level domain ICANN reserves for private networks | Every container's network name, where core's [conventions](https://github.com/VeoveoAI/veoveo-core/blob/main/docs/CONVENTIONS.md#http-paths) allow plain HTTP |
| Lore v0.10.1 from [VeoveoAI/lore](https://github.com/VeoveoAI/lore) at `36808dd` | Version control for environments over `lores://`: gRPC over TLS on TCP 41337 and Lore's storage protocol over QUIC, RFC 9000, on UDP 41337. The server runs as Epic ships it; the client carries the two patches of D41 |
| OAuth 2.0 client credentials, RFC 6749 §4.4, with RFC 7523 assertions and RFC 8707 resources | How the Lore token service obtains each environment's token from the Gateway |
| JWT access tokens, RFC 9068 | Lore tokens with the `lore_resources` claim, profiled in the Gateway's [Lore tokens](https://github.com/VeoveoAI/veoveo-service-gateway/blob/main/crates/veoveo-service-gateway/DESIGN.md#lore-tokens) |
| [Component lock](https://github.com/VeoveoAI/veoveo-core/blob/main/platform/installation/contract/DESIGN.md), `https://veoveo.ai/formats/component-lock` | `component-lock.json`, the revision of each component the installation builds and snapshots into Lore |

Two interfaces are internal to this installation and carry no compatibility promise:
the Lore token file, which the token service writes and the patched Lore client reads,
and `/etc/lore/sandbox.toml`, which names the one server the client may reach.

## Services

| Service | Image | Networks | Purpose |
|---|---|---|---|
| `vv-postgres` | PostgreSQL 18.6 by digest | `vv-local`, `vv-outside` | The installation database |
| `vv-seaweedfs` | SeaweedFS 4.48 by digest | `vv-local`, `vv-outside` | The object store |
| `vv-egress` | Envoy 1.40.0 by digest | `vv-local`, `vv-media`, `vv-outside` | The edge |
| `vv-lore` | built from `lore/Dockerfile` | `vv-local` | The Lore server, storing on its volume |
| `vv-lore-tokens` | the Gateway's `runtime` image | `vv-local` | The Gateway's `lore-tokens` command, as root |
| `vv-lore-admin` | the environment layer over Debian | `vv-local` | Creates repositories from snapshots, records later snapshots and merges, as Lore's service account |
| `vv-srv-gateway`, `vv-mcp-time`, `vv-mcp-artifact`, `vv-mcp-media` | the environment layer over each component's `dev` image | `vv-local`, and `vv-media` for Media | The environments |
| `vv-tunnel` | cloudflared 2026.10.0 by digest | host | The public origin's tunnel, optional |

PostgreSQL, SeaweedFS and the edge start by default. The `envs` profile adds Lore, its
token service, its admin and the environments, all of which depend on the Gateway.

## Environments

The environment layer, `envs/Dockerfile`, turns a component's `dev` image into an
environment. It installs the patched Lore client setgid to the `lore-cred` group, adds
the installation CA to the system trust store, writes `/etc/lore/sandbox.toml` naming
`lores://vv-lore.internal:41337`, creates `/sandbox` for the `sandbox` user, and removes
the setuid and setgid bits of every other program. An environment runs as `sandbox`
with every capability dropped, keeps `/sandbox` in a named volume and does nothing until
a command runs in it.

An environment compiles its component from its Lore working copy at `/sandbox/src`.
The served binary builds into `/sandbox/target-serve` and runs from there, apart from
`target/`, where acceptance builds enable test-only features. The volume keeps the
working copy, both build directories and the component's state through a recreation.
Images are built on the host, and no Docker socket enters an environment.

Environments run without `no-new-privileges`, because the kernel ignores the Lore
client's setgid bit under it. The layer's removal of every other setuid and setgid
program keeps that from opening a path to root. A process started under
`no-new-privileges` inside an environment, such as a coding agent's own command
sandbox, cannot read the Lore token.

## Networks And Names

`vv-local`, `10.231.10.0/24`, is an internal network that no route leaves. The
environments, Lore, PostgreSQL and SeaweedFS share it, and each answers under its
`.internal` name, such as `vv-mcp-time.internal`. `vv-media`, `10.231.11.0/24`, is also
internal and holds only Media's environment and the edge. `vv-outside` is an ordinary
bridge network for the edge and the infrastructure's published ports.

An environment reaches PostgreSQL, the object store, Lore and the other environments
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

The Gateway issues Lore tokens. `generate-local-installation` writes a Lore client and
key for each environment and for the admin into the Gateway environment's state, and the
installation grants each environment's client its component's repository after the
repositories exist. `vv-lore-tokens` mounts that state read-only and each environment's
token volume, and every ten minutes writes a 15-minute token to `/run/lore/token`: owned
by root, group `lore-cred`, mode 0640, in a directory of mode 0750. The environment
mounts its token volume read-only.

The patched client, run by any user in an environment, reads `/etc/lore/sandbox.toml`
and the token while it holds `lore-cred`. It then drops the group for good, makes itself
undumpable and clears every environment variable outside a short allowlist. It sends the
token only to the configured server's scheme, host and port, and refuses token flags
and Lore's service mode. A token file that the agent could read without the group stops
the client.

The Lore server reads the Gateway's keys at startup, so the Gateway runs before Lore,
and the Gateway environment's first source is its GitHub snapshot. Once its repository
exists, the environment replaces that checkout with its Lore clone of the same files.

## Coding Agents

An agent in an environment works in `/sandbox/src`, builds and tests with Cargo
through the edge's proxy, and pushes branches with `lore`, which acts as the
environment's Lore client. It reaches no credential: the Lore token, the registration
secret and the provider key stay outside its reach, and it holds no GitHub credential.

The installation does not yet run an agent. No image installs an agent CLI, the edge
has no route to a model provider and adds no model API key, and the README describes no
way to start or attach an agent. That route belongs at the edge like the provider's, a
`.internal` name that adds the key, so the agent holds a placeholder.

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

## Gaps

- Coding agents do not run yet, as [Coding Agents](#coding-agents) describes.
- The real media provider through `media-provider.internal` is configured and was not
  qualified with a billed run; the egress tests qualified the route with a stand-in.
- The Linux host has not run this installation, and GPU environments wait for the GPU
  components.
- The Gateway environment holds every Lore client key, the admin's included, with the
  installation's other secrets; an agent working there has the Gateway's authority.
- Lore's gRPC and QUIC verify the server against the installation CA by name; the
  client does not pin the server's certificate.
