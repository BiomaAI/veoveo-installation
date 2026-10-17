# Native OpenShell Setup

This is the local macOS first path. Homebrew owns the unmodified OpenShell 0.1.4
CLI and gateway. The configured supervisor image adds the reviewed HTTP/2/gRPC
credential path; no second gateway or application launcher is required.

`component-lock.json` records source revisions and the images used for local
acceptance. Machine-local image IDs are evidence, not portable registry releases.
The factory CLI uses the maintained sibling `lore/` checkout's auth-only patches;
the running Lore server is a pinned v0.10.1 extension build with a small native
pre-push hook. The broad authoring-authorization patch was reverted; no custom
claims, RPC middleware or stream-expiry behavior remain. Changes have not yet
been published as an upstream PR or portable image release.

Next implementation: [direct IdP Lore credentials](../../veoveo-docs/LORE_DIRECT_OIDC_PLAN.md)
using native provider refresh. Desktop is no longer an acceptance requirement.
The manual signer-based commands below record the current pre-cutover test path;
they must be replaced, not expanded into a renewal service. The new path is not
yet deployed or qualified by this documentation change.

## Operator State And Identity

The native gateway reads `~/.config/openshell/gateway.toml` and `gateway.env`.
The installation copy of `gateway.toml` selects the Docker driver, verified HTTPS,
OIDC and fail-closed policy admission. `gateway.env` pins the supervisor and official
sandbox-runtime images, disables telemetry, and names the operator CA bundle.
The native gateway database and credential store remain outside all workloads.

`../identity/configure-openshell` configures the permanent local Keycloak clients.
It retains their standard `basic`, `profile` and `roles` scopes, the CLI's optional
`offline_access`, and an exact HTTP loopback callback path with PKCE. Keycloak's
native loopback matching permits the CLI's dynamic callback port. The runtime SDK
itself uses generic OIDC discovery, not Keycloak administration.

Private controller and nonmember acceptance credentials live in ignored
`state/openshell/`, mode 0600, under a private directory. Neither enters a factory,
service, image, Compose environment or log. The native human CLI uses its own PKCE
login and refresh storage, not the controller credential.

On each Mac, complete the one-time [installation CA trust setup](../identity/README.md#macos-certificate-trust)
before the first login. The native CLI then uses macOS trust for the private issuer
from every terminal, including automatic OIDC refresh. No shell certificate export
is required:

```sh
openshell gateway login openshell
openshell status
openshell sandbox list --all-workspaces
openshell whoami
```

The CA-only file at `~/.config/openshell/gateways/openshell/mtls/ca.crt` is the native
CLI's separate gateway transport trust location. Keep that registration trust in
place as well. The registration uses OIDC; no client certificate or insecure TLS
flag is needed. The service's `gateway.env` remains separate from terminal setup.

Installation acceptance runs these commands from a new shell with `SSL_CERT_FILE`
and `SSL_CERT_DIR` absent, then repeats an authenticated command after the stored
OIDC access token expires to verify automatic refresh. For an existing shell,
`env -u SSL_CERT_FILE -u SSL_CERT_DIR openshell status` explicitly checks native
trust. CLI OIDC refresh is separate from the factory's Lore grant renewal gate.

## Build Inputs

Build the supervisor from the locked OpenShell revision using its native prebuilt
binary/image workflow. Wait for the cross-build to complete before staging the
binary. The upstream image recipe is `deploy/docker/Dockerfile.supervisor`.
Then add the installation's public CA through `Supervisor.Dockerfile`:

```sh
docker build --build-context ca=./tls/ca \
  -f openshell/Supervisor.Dockerfile -t veoveo/supervisor:local .
```

Archive the exact locked Lore client revision into ignored
`state/openshell/lore-source/`, then build the client and factory:

```sh
docker build -f factory/Lore.Dockerfile \
  --build-context lore-source=./state/openshell/lore-source \
  -t veoveo/lore-client:local .
docker build --build-context lore=docker-image://veoveo/lore-client:local \
  --build-context ca=./tls/ca -t veoveo/factory:local factory
```

The server uses the same `factory/Lore.Dockerfile` recipe, with the exact locked
server revision archived in `state/openshell/lore-hook-source/`. Compose builds
its `runtime` target from this separate source snapshot. The older client snapshot
keeps the accepted factory CLI/image unchanged. To export the optional operator-only
disposable fixture seeder (not shipped in the server image):

```sh
docker build -f factory/Lore.Dockerfile --target fixture \
  --build-context lore-source=./state/openshell/lore-hook-source \
  --output type=local,dest=./state/openshell/factory-hook-bin .
```

The factory starts from a pinned Rust image and contains OpenCode 2.0.29. Its
DeepInfra/MiMo settings are present; the first Lore-only fixture deliberately has
no inference provider attached and makes no model requests.

## Focused Native SDK Acceptance

Build `first-path` in the sibling qualification repository:

```sh
cargo build --locked --features first-path --bin first-path
```

Its `--installation` option names this installation directory. `factory --image`
creates the initial factory/provider; `factory --replace --image` replaces only
that disposable test factory after an image rebuild. Use image digests/IDs when
recording a deployed version. It does not publish or build agent-authored images.

`provision-lore --repository ID` uses the trusted adapter signer to provision one
fifteen-minute test grant. The sandbox's OpenShell RPC policy makes this smoke path
read-only; an empty native Lore action array alone does not. It never prints the
token. `first-path sync-factory` updates the native provider and policy and waits for supervisor
installation. A new Lore read after rotation does not require a factory restart.
This bootstrap helper is not an automatic renewal service.

The `lore` action checks assigned and unassigned repositories. `boundaries` checks
credential custody, protected paths and raw TCP egress. `service --image` recreates
the MCP fixture in `vv-first-private`; `--reuse` only checks the existing instance.
`service-recreation --image` checks two replacements against a same-named default
workspace sentinel and removes only a sentinel it created itself.

Lore's private endpoint is recorded in `bootstrap.json`; it must match the factory
policy, trusted leaf certificate IP SAN and the bootstrap service's fixed address.
No host port is published for that server. Desktop remains on its existing verified
remote `grpcs://localhost:7443`.

The fixture serves MCP initialization, discovery and echo through authenticated
native `ForwardTcp`. Its fake application bearer is separate from OIDC management
authentication. A nonmember gets the native `NOT_FOUND` concealment response.

Full branch/revision deployment, arbitrary composition, infrastructure migration,
Linux/CUDA and the direct credential cutover are tracked in the
[hard-cut plan](../../veoveo-docs/OPENSHELL_HARDCUT_PLAN.md).

## Normal Lore Push Guard

`lore/server.toml` enables the existing `factory_branch` pre-push hook with an empty
assignment map. The trusted installation/integration fills it with designated
factories' **verified** identity claims and stable repository/branch IDs. The agent
cannot edit this server configuration. See the [hook contract and configuration](../../lore/docs/reference/factory-branch-hook.md).
Unassigned humans retain ordinary permissions. Issue ordinary repository credentials
with `is_service_account = false`; automation alone never grants a protection bypass.
The existing hook calls cover both push APIs. Wrong-branch pushes use the existing
`FailedPrecondition` workflow rejection so normal clients display both branch IDs.

For the disposable acceptance fixture, stop the owning Lore server and take a
consistent private backup of its data volume before opening its stores. Run the
exported `factory-branch-fixture /data` with that volume mounted in an isolated
operator container, never in an agent workload. It creates fresh repository/branch
IDs, valid empty revision heads, and native protected `main`. Save its final JSON
line privately as `state/openshell/factory-hook-fixture.json`. Configure
`veoveo-hook-factory` to its `assigned` ID and `veoveo-hook-protected` to its `main`
ID before restarting Lore. Do not expose the seeder as a server API or add these
test repositories to the Desktop catalog.

Run `first-path --installation INSTALLATION factory-hook --image FACTORY_IMAGE`.
It uses an ordinary short-lived repository grant in a temporary native provider,
clones, commits a tiny edit, pushes and verifies content in an independent clone.
It prepares a real commit on `other-author` before asserting the explicit hook
rejection. It also checks native protected-branch behavior and an unassigned human
push. The stock CLI renders native protected-branch denial as a generic authorization
error; the fixture reads the protection metadata and verifies unchanged remote
content. Native push-handler tests independently check the `protected` status.
Temporary workload/provider/profile/workspace setup and the workflow share cleanup;
only admitted resources from this run are removed. A pre-existing workspace is refused.
Restore the empty trusted assignment map after qualification and restart Lore.

The run writes a private `state/openshell/factory-hook-result.json` only after all
checks and cleanup pass. It makes no inference calls and leaves the original smoke
path read-only. This is a normal-push workflow guard, not complete isolation against
all storage or administration APIs. Manual test-provider updates do **not** qualify
automatic renewal or revocation; those remain separate OpenShell lifecycle gates.
