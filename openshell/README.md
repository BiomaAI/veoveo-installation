# Native OpenShell Setup

This is the local macOS first path. Homebrew owns the unmodified OpenShell 0.1.4
CLI and gateway. The configured supervisor image adds the reviewed HTTP/2/gRPC
credential path; no second gateway or application launcher is required.

`component-lock.json` records source revisions and the images used for local
acceptance. Machine-local image IDs are evidence, not portable registry releases.
The factory CLI uses the maintained sibling `lore/` checkout's auth-only patches;
the running Lore server is the pinned upstream release. Fork changes have not yet
been published as an upstream PR or portable image release.

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

For the private local issuer, give the CLI the installation's combined CA bundle:

```sh
export SSL_CERT_FILE="$PWD/state/openshell/ca-bundle.pem"
openshell gateway login openshell
openshell sandbox list
openshell --workspace vv-first-private sandbox list
```

The CA-only file at `~/.config/openshell/gateways/openshell/mtls/ca.crt` is the native
CLI's gateway transport trust location. The registration uses OIDC; no client
certificate or insecure TLS flag is needed.

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
read-only, fifteen-minute test grant. It never prints the token. `first-path
sync-factory` updates the native provider and policy and waits for supervisor
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
Linux/CUDA and Desktop graph/session recovery are tracked in the
[hard-cut plan](../../veoveo-docs/OPENSHELL_HARDCUT_PLAN.md).
