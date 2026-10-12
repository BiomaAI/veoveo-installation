# veoveo-template-installation

A Veoveo installation is one repository that records what an organization runs: its
domain, identity providers, tenants, who holds which roles, and which components it
runs at which revisions. Create yours from this template with **Use this template**,
named `veoveo-<installation>` in your organization, for example `BiomaAI/veoveo-bioma`.

Components register themselves with the Gateway and declare their own permissions, so
an installation names no server's internals. It decides only who may do what.

The defaults run a local installation on one workstation: PostgreSQL in Docker Compose,
and each component in its own OpenShell environment.

## Contents

| Path | Purpose |
|---|---|
| `compose.yaml` | PostgreSQL 18.6, pinned by digest and published on the loopback interface only |
| `postgres/initdb/owner.sql` | Creates the installation owner `veoveo_owner` and its database `veoveo` when the data directory is new |
| `openshell/providers/vv-registration.yaml` | The OpenShell provider profile that carries the installation's registration secret into environments as a placeholder |

The installation owner owns the database and may create roles, and it is not a
superuser. The Gateway connects as the owner, applies the kernel migrations and gives
each registered server its own login and schema.

## Local Installation

Requirements: Docker with Compose v2, and OpenShell 0.1.3 with a local gateway started
with `OPENSHELL_TELEMETRY_ENABLED=false`. On macOS, Docker Desktop 4.94 or newer with
host networking enabled. Each component repository documents its own environment; the
steps below run them together. Run them from this repository's directory.

1. Keep `VEOVEO_POSTGRES_PASSWORD` (the superuser's), `VEOVEO_DATABASE_PASSWORD` (the
   installation owner's) and, optionally, `VEOVEO_DATABASE_PORT` (5432 by default) in an
   uncommitted `.env` file next to `compose.yaml`, then start the database:

   ```sh
   umask 077
   printf 'VEOVEO_POSTGRES_PASSWORD=%s\nVEOVEO_DATABASE_PASSWORD=%s\n' \
     "$(openssl rand -hex 24)" "$(openssl rand -hex 24)" > .env
   docker compose up -d --wait
   ```

2. Create the Gateway environment from
   [veoveo-service-gateway](https://github.com/VeoveoAI/veoveo-service-gateway): build its
   `dev` image, create `vv-srv-gateway` with its `openshell/policy.yaml`, and clone its
   source into `/sandbox/src`. Give it the installation owner's password, and only that
   one, then generate the installation once:

   ```sh
   owner=$(mktemp) && grep '^VEOVEO_DATABASE_PASSWORD=' .env > "$owner"
   openshell sandbox exec vv-srv-gateway -- mkdir -p /sandbox/state/gateway
   openshell sandbox upload vv-srv-gateway "$owner" /sandbox/state/database.env
   rm -f "$owner"
   openshell sandbox exec vv-srv-gateway -- bash -lc 'chmod 600 /sandbox/state/database.env \
     && cd /sandbox/src && cargo build --locked --bin veoveo-service-gateway \
     && target/debug/veoveo-service-gateway generate-local-installation \
          --directory /sandbox/state/gateway --issuer http://host.openshell.internal:8080'
   ```

   Then start the Gateway in its own terminal and forward port 8080, as its README's
   Local Launch section shows.

3. Load the generated registration secret into an OpenShell provider without printing
   it:

   ```sh
   openshell profile import -f openshell/providers/vv-registration.yaml --global
   VEOVEO_REGISTRATION_SECRET="$(openshell sandbox exec vv-srv-gateway -- bash -c \
     '. /sandbox/state/gateway/gateway.env && printf %s "$VEOVEO_REGISTRATION_SECRET"')" \
     openshell provider create --name vv-registration --type vv-registration \
       --credential VEOVEO_REGISTRATION_SECRET
   ```

4. Create the Time environment from
   [veoveo-mcp-time](https://github.com/VeoveoAI/veoveo-mcp-time) with the provider
   attached, clone its source into `/sandbox/src`, then start Time in its own terminal
   and forward port 8800, as its README shows. Time registers itself with the Gateway
   at startup.

5. To run Time's acceptance tests, copy the callers' keys from the Gateway environment
   into `/sandbox/acceptance` in the Time environment and follow the Acceptance section
   of Time's README:

   ```sh
   keys=$(mktemp -d) && chmod 700 "$keys"
   for f in acceptance-member acceptance-admin; do
     for e in pem jwks.json; do
       openshell sandbox download vv-srv-gateway /sandbox/state/gateway/$f.$e "$keys/"
       openshell sandbox upload vv-mcp-time "$keys/$f.$e" /sandbox/acceptance/$f.$e
     done
   done
   rm -rf "$keys"
   openshell sandbox exec vv-mcp-time -- bash -c 'chmod 700 /sandbox/acceptance && chmod 600 /sandbox/acceptance/*.pem'
   ```

Environments reach the database and each other through `host.openshell.internal`, which
OpenShell 0.1.3 maps to the host's loopback interface on macOS and on Linux, so the
database and every forward stay on `127.0.0.1`. Each component's policy names the
endpoints it may reach. Names follow the Veoveo
[naming and format conventions](https://github.com/VeoveoAI/veoveo-core/blob/main/docs/CONVENTIONS.md).

## Stop

Stop each service with Ctrl-C in its terminal, or from the host, then remove the
forwards and stop the database. The data stays in the `vv-local_vv-postgres` volume,
and the steps above start the installation again:

```sh
openshell sandbox exec vv-mcp-time -- pkill -TERM -f '^/sandbox/run/veoveo-mcp-time-'
openshell sandbox exec vv-srv-gateway -- pkill -TERM -f '^/sandbox/run/veoveo-service-gateway-'
openshell forward stop 8800 vv-mcp-time
openshell forward stop 8080 vv-srv-gateway
docker compose stop
```

Time removes its registration when it receives SIGTERM.

## Reset

A server's key lives in its environment, and the Gateway pins a namespace to the first
key that registers it. A recreated environment has a new key, so its server needs a
fresh namespace claim, which a reset of the database provides. After the steps in Stop,
remove the database volume, the environments, and the registration provider and its
profile, then start again from step 1:

```sh
docker compose down -v
openshell sandbox delete vv-mcp-time vv-srv-gateway
openshell provider delete vv-registration
openshell profile delete vv-registration --global
```

## License

Apache-2.0. See [LICENSE](LICENSE).
