# veoveo-template-installation

A Veoveo installation is one repository that records what an organization runs: its
domain, identity providers, tenants, who holds which roles, and which components it
runs at which revisions. Create yours from this template with **Use this template**,
named `veoveo-<installation>` in your organization, for example `BiomaAI/veoveo-bioma`.

Components register themselves with the Gateway and declare their own permissions, so
an installation names no server's internals. It decides only who may do what.

The defaults run a local installation on one workstation: PostgreSQL and the RustFS
object store in Docker Compose, and each component in its own OpenShell environment.

## Contents

| Path | Purpose |
|---|---|
| `component-lock.json` | The repository and Git revision of each component the installation runs, in core's [component lock](https://github.com/VeoveoAI/veoveo-core/blob/main/platform/installation/contract/DESIGN.md) format |
| `compose.yaml` | PostgreSQL 18.6 and RustFS 1.0.1, each pinned by digest and published on the loopback interface only, and cloudflared 2026.10.0 under the optional `tunnel` profile |
| `postgres/initdb/owner.sql` | Creates the installation owner `veoveo_owner` and its database `veoveo` when the data directory is new |
| `openshell/providers/vv-registration.yaml` | The OpenShell provider profile that carries the installation's registration secret into environments as a placeholder |

The installation owner owns the database and may create roles, and it is not a
superuser. The Gateway connects as the owner, applies the kernel migrations and gives
each registered server its own login and schema. The Artifact server holds the object
store's credential and signs every request that moves bytes, so clients send and fetch
bytes at the object store directly.

## Local Installation

Requirements: Docker with Compose v2, `jq`, and OpenShell 0.1.3 with a local gateway
started with `OPENSHELL_TELEMETRY_ENABLED=false`. On macOS, Docker Desktop 4.94 or newer
with host networking enabled. Each component repository documents its own environment;
the steps below run them together. Run them from this repository's directory.

Every environment runs the revision `component-lock.json` names. To check one out, clone
the component's repository into its environment and detach at the locked revision, for
example for the Gateway:

```sh
rev=$(jq -er '.components[] | select(.name == "veoveo-service-gateway") | .revision' component-lock.json)
openshell sandbox exec vv-srv-gateway -- git clone --quiet https://github.com/VeoveoAI/veoveo-service-gateway /sandbox/src
openshell sandbox exec vv-srv-gateway -- git -C /sandbox/src checkout --quiet --detach "$rev"
```

The environment's `dev` image and its `openshell/policy.yaml` come from the same
revision. To move a component to a new revision, change it in `component-lock.json`,
commit, then run `git -C /sandbox/src fetch --quiet` and the same checkout in its
environment and restart it. When the new revision changes the policy, apply it to the
running environment first with `openshell policy set <environment> --policy <file> --wait`.

1. Keep `VEOVEO_POSTGRES_PASSWORD` (the superuser's), `VEOVEO_DATABASE_PASSWORD` (the
   installation owner's), `VEOVEO_STORAGE_ACCESS_KEY` and `VEOVEO_STORAGE_SECRET_KEY`
   (the object store's credential) and, optionally, `VEOVEO_DATABASE_PORT` (5432 by
   default) and `VEOVEO_STORAGE_PORT` (9000 by default) in an uncommitted `.env` file
   next to `compose.yaml`, then start PostgreSQL and RustFS. The commands below write
   new credentials and keep every other setting in `.env`, such as those of the
   [public origin](#public-origin):

   ```sh
   umask 077
   touch .env
   grep -v -E '^VEOVEO_(POSTGRES_PASSWORD|DATABASE_PASSWORD|STORAGE_ACCESS_KEY|STORAGE_SECRET_KEY)=' .env > .env.next
   printf 'VEOVEO_POSTGRES_PASSWORD=%s\nVEOVEO_DATABASE_PASSWORD=%s\nVEOVEO_STORAGE_ACCESS_KEY=%s\nVEOVEO_STORAGE_SECRET_KEY=%s\n' \
     "$(openssl rand -hex 24)" "$(openssl rand -hex 24)" "$(openssl rand -hex 12)" "$(openssl rand -hex 24)" >> .env.next
   mv .env.next .env
   docker compose up -d --wait
   ```

2. Create the Gateway environment from
   [veoveo-service-gateway](https://github.com/VeoveoAI/veoveo-service-gateway): build its
   `dev` image, create `vv-srv-gateway` with its `openshell/policy.yaml`, and check out its
   locked revision into `/sandbox/src`. Give it the installation owner's password, and only that
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

   The generated configuration has no policy rules. The installation lets
   `acceptance-admin` make administrative reads, such as the cost views and server
   health, with one rule:

   ```sh
   config=$(mktemp -d)
   openshell sandbox download vv-srv-gateway /sandbox/state/gateway/gateway.json "$config/"
   jq '.policies[0].rules = [{id: "administrative-reads", effect: "allow", actions: ["admin_read"],
         principalIds: [.authorizationServers[0].issuer + "#acceptance-admin"]}]' \
     "$config/gateway.json" > "$config/rules.json"
   openshell sandbox upload vv-srv-gateway "$config/rules.json" /sandbox/state/gateway/gateway.json
   rm -f "$config/gateway.json" "$config/rules.json" && rmdir "$config"
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
   attached, check out its locked revision into `/sandbox/src`, then start Time in its own terminal
   and forward port 8800, as its README shows. Time registers itself with the Gateway
   at startup.

5. Create the Artifact environment from
   [veoveo-mcp-artifact](https://github.com/VeoveoAI/veoveo-mcp-artifact) with the
   provider attached and check out its locked revision into `/sandbox/src`. Artifact
   signs transfers with the object store's credential itself, so it receives that
   credential, and only that one, as an owner-only file:

   ```sh
   storage=$(mktemp) && grep -E '^VEOVEO_STORAGE_(ACCESS|SECRET)_KEY=' .env > "$storage"
   openshell sandbox exec vv-mcp-artifact -- mkdir -p /sandbox/state
   openshell sandbox upload vv-mcp-artifact "$storage" /sandbox/state/storage.env
   rm -f "$storage"
   openshell sandbox exec vv-mcp-artifact -- chmod 600 /sandbox/state/storage.env
   ```

   Then start Artifact in its own terminal and forward port 8801, as its README's
   Running Artifact section shows. Artifact prepares its bucket and registers itself
   with the Gateway at startup. With a [public origin](#public-origin), start it with
   `VEOVEO_SHARE_BASE_URL` set to that origin, so share links name it.

6. Create the Media environment from
   [veoveo-mcp-media](https://github.com/VeoveoAI/veoveo-mcp-media) with the provider
   attached and check out its locked revision into `/sandbox/src`. The local
   installation runs Media against its fake provider, which shares a webhook secret
   with Media. Both values live in an owner-only file the environment generates:

   ```sh
   openshell sandbox exec vv-mcp-media -- bash -lc 'mkdir -p /sandbox/state && umask 077 \
     && printf "MEDIA_PROVIDER_API_KEY=fake\nMEDIA_PROVIDER_WEBHOOK_SECRET=whsec_%s\n" \
          "$(head -c 24 /dev/urandom | od -An -tx1 | tr -d " \n")" > /sandbox/state/media.env'
   ```

   Then start the fake provider on `127.0.0.1:8803` and Media in their own terminals and
   forward port 8802, as its README's Running Media section shows. Media registers
   itself with the Gateway at startup. With `VEOVEO_PUBLIC_ORIGIN` set to
   `http://127.0.0.1:8802`, Media's own listener, the fake provider posts each outcome to
   Media's callback route; without it, runs complete through status checks of the fake.

7. To run the acceptance tests of Time, Artifact and Media, copy the callers' keys from
   the Gateway environment into `/sandbox/acceptance` in each environment and follow the
   Acceptance section of each README:

   ```sh
   keys=$(mktemp -d) && chmod 700 "$keys"
   for f in acceptance-member acceptance-admin; do
     for e in pem jwks.json; do
       openshell sandbox download vv-srv-gateway /sandbox/state/gateway/$f.$e "$keys/"
       for env in vv-mcp-time vv-mcp-artifact vv-mcp-media; do
         openshell sandbox upload $env "$keys/$f.$e" /sandbox/acceptance/$f.$e
       done
     done
   done
   rm -f "$keys"/acceptance-* && rmdir "$keys"
   for env in vv-mcp-time vv-mcp-artifact vv-mcp-media; do
     openshell sandbox exec $env -- bash -c 'chmod 700 /sandbox/acceptance && chmod 600 /sandbox/acceptance/*.pem'
   done
   ```

Environments reach the database, the object store and each other through
`host.openshell.internal`, which OpenShell 0.1.3 maps to the host's loopback interface on
macOS and on Linux, so the database, the object store and every forward stay on
`127.0.0.1`. Each component's policy names the endpoints it may reach. Artifact signs
its URLs for `http://host.openshell.internal:9000`, so a browser on the host fetches them
only when the host maps `host.openshell.internal` to `127.0.0.1`. Names follow the Veoveo
[naming and format conventions](https://github.com/VeoveoAI/veoveo-core/blob/main/docs/CONVENTIONS.md).

## Public Origin

An installation has one public origin, such as `https://veoveo.example.com`, and serves
each public route under its own path. The local installation publishes the two routes
that callers without an account use: the media provider's callbacks under
`/media/operations/` and Artifact's share links under `/artifact/shares/`.

The optional `tunnel` Compose profile connects the origin to the workstation through a
remote-managed [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/).
Create the tunnel with a proxied DNS record for the origin's host and these ingress
rules, in this order:

| Path | Service | Origin Host header |
|---|---|---|
| `^/media/operations/` | `http://127.0.0.1:8802` | `host.openshell.internal:8802` |
| `^/artifact/shares/` | `http://127.0.0.1:8801` | `host.openshell.internal:8801` |
| Any other | `http_status:404` | |

Each server accepts requests only for the host it registers at, so the tunnel sends that
host. Add the origin as `VEOVEO_PUBLIC_ORIGIN` and the tunnel's connector token as
`VEOVEO_TUNNEL_TOKEN` to `.env`, then start the tunnel:

```sh
docker compose --profile tunnel up -d vv-tunnel
```

Artifact's share links then name the origin. Its acceptance tests open them from inside
the environment, which reaches the origin once its policy admits it for them:

```sh
host=$(sed -n 's#^VEOVEO_PUBLIC_ORIGIN=https://\([^/:]*\).*#\1#p' .env)
openshell policy update vv-mcp-artifact --add-endpoint "$host:443" \
  --rule-name public_origin --binary '/sandbox/run/acceptance-*/**' --wait
```

## Stop

Stop each service with Ctrl-C in its terminal, or from the host, then remove the
forwards and stop PostgreSQL, RustFS and the tunnel. The data stays in the
`vv-local_vv-postgres` and `vv-local_vv-rustfs` volumes, and the steps above start the
installation again:

```sh
openshell sandbox exec vv-mcp-media -- pkill -TERM -f '^/sandbox/run/veoveo-mcp-media-'
openshell sandbox exec vv-mcp-artifact -- pkill -TERM -f '^/sandbox/run/veoveo-mcp-artifact-'
openshell sandbox exec vv-mcp-time -- pkill -TERM -f '^/sandbox/run/veoveo-mcp-time-'
openshell sandbox exec vv-srv-gateway -- pkill -TERM -f '^/sandbox/run/veoveo-service-gateway-'
openshell forward stop 8802 vv-mcp-media
openshell forward stop 8801 vv-mcp-artifact
openshell forward stop 8800 vv-mcp-time
openshell forward stop 8080 vv-srv-gateway
docker compose --profile tunnel stop
```

The first command stops Media and its fake provider. Time, Artifact and Media remove
their registrations when they receive SIGTERM.

## Reset

A server's key lives in its environment, and the Gateway pins a namespace to the first
key that registers it. A recreated environment has a new key, so its server needs a
fresh namespace claim, which a reset of the database provides. After the steps in Stop,
remove the database and object store volumes, the environments, and the registration
provider and its profile, then start again from step 1. Compose reads every variable
`compose.yaml` requires even to remove the services, so an `.env` that holds no object
store credential gets a placeholder one first; step 1 writes new credentials:

```sh
grep -q '^VEOVEO_STORAGE_SECRET_KEY=' .env || printf 'VEOVEO_STORAGE_ACCESS_KEY=reset\nVEOVEO_STORAGE_SECRET_KEY=reset\n' >> .env
docker compose --profile tunnel down -v
openshell sandbox delete vv-mcp-media vv-mcp-artifact vv-mcp-time vv-srv-gateway
openshell provider delete vv-registration
openshell profile delete vv-registration --global
```

## License

Apache-2.0. See [LICENSE](LICENSE).
