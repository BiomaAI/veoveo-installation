# veoveo-template-installation

A Veoveo installation is one repository that records what an organization runs: its
domain, identity providers, tenants, who holds which roles, and which components it
runs at which revisions. Create yours from this template with **Use this template**,
named `veoveo-<installation>` in your organization, for example `BiomaAI/veoveo-bioma`.

Components register themselves with the Gateway and declare their own permissions, so
an installation names no server's internals. It decides only who may do what.

The defaults run the trusted local installation with Docker Compose. Its `envs`
containers hold running components and private runtime state. **Never run coding
agents in those containers.** The `autonomy` profile adds separate `vv-dev-*`
containers, each with its own source volume and internal network. OpenCode v2 uses
MiMo through Envoy and commits work with Lore. Secrets stay in trusted services.

## Contents

| Path | Purpose |
|---|---|
| `DESIGN.md` | How the installation's environments, edge and Lore fit together, and what remains open |
| `component-lock.json` | The repository and Git revision of each component the installation runs, in core's [component lock](https://github.com/VeoveoAI/veoveo-core/blob/main/platform/installation/contract/DESIGN.md) format |
| `compose.yaml` | PostgreSQL 18.6, SeaweedFS 4.48 (`weed mini`) and Envoy 1.40.0, each pinned by digest; the Lore server, the Lore token service, the Lore admin container and the environments under the `envs` profile; cloudflared 2026.10.0 under the `tunnel` profile |
| `envs/Dockerfile` | Legacy trusted bootstrap/runtime tooling; never an agent sandbox |
| `autonomy/` | Isolated dev images, pinned OpenCode v2, managed config, Envoy routes and credential provisioning |
| `lore/Dockerfile`, `lore/server.toml` | Lore built from [VeoveoAI/lore](https://github.com/VeoveoAI/lore) at one commit, and the server's settings |
| `egress/envoy.yaml`, `egress/render`, `egress/sds/` | The edge's configuration, the script that fills in the hosts `.env` names, and the files that point Envoy at its secrets |
| `postgres/initdb/owner.sql` | Creates the installation owner `veoveo_owner` and its database `veoveo` when the data directory is new |

The installation owner owns the database and may create roles, and it is not a
superuser. The Gateway connects as the owner, applies the kernel migrations and gives
each registered server its own login and schema. The Artifact server holds the object
store's credential and signs every request that moves bytes, so clients send and fetch
bytes at the object store directly.

## Networks And Names

Every container answers under `.internal`, the top-level domain ICANN reserves for
private networks, where a local installation may use plain HTTP:

| Name | What answers |
|---|---|
| `vv-gateway.internal:8080` | The edge, in front of the Gateway |
| `vv-egress.internal:3128` | The edge's HTTPS proxy |
| `vv-lore.internal:41337` | The Lore server, over `lores://` with the installation CA |
| `vv-postgres.internal:5432`, `vv-seaweedfs.internal:9000` | PostgreSQL and the object store |
| `vv-srv-gateway.internal:8080`, `vv-mcp-time.internal:8800`, `vv-mcp-artifact.internal:8801`, `vv-mcp-media.internal:8802` | The Gateway and each server in its environment |
| `media-provider.internal` | The edge's route to the media provider's API, on Media's network only |

Environments, Lore and the infrastructure share `vv-local`, an internal network that no
route leaves. Media's environment also joins `vv-media`, where the provider's route
answers. The edge joins both and `vv-outside`, and it is the environments' only way out:

- **Inbound:** it publishes the Gateway and the servers on the host's loopback
  interface, at `127.0.0.1:8080` and `127.0.0.1:8800` to `8802`, where the tunnel and
  the host's tools reach them.
- **HTTPS:** an environment reaches the internet only through its proxy at
  `vv-egress.internal:3128`. The proxy reaches the Rust toolchain, crates.io and GitHub,
  and the hosts `.env` names.
- **Secrets:** the edge adds the registration secret to `POST /oauth/register` at
  `vv-gateway.internal`, and the media provider's key at `media-provider.internal`.
  An environment holds a placeholder and never reads either secret.

The `envs` profile below is trusted bootstrap/runtime tooling. It retains the older
setgid Lore client for compatibility. The `autonomy` profile uses ordinary mode-0755
Lore over authenticated Envoy gRPC routes, with `no-new-privileges` enabled. Agents
never share a filesystem, PID namespace or network with runtime services.

PostgreSQL also publishes `127.0.0.1:5432`, and SeaweedFS `127.0.0.1:9000` and its
admin UI at `http://127.0.0.1:23646`, user `admin`. Artifact signs its URLs for
`http://vv-seaweedfs.internal:9000`, so a browser on the host fetches them once the host
maps `vv-seaweedfs.internal` to `127.0.0.1`. Host tools that request Gateway tokens map
`vv-gateway.internal` the same way.

## Lore

Lore is the installation's version control (D41). Each component has one Lore
repository, which starts from a snapshot of its locked GitHub revision. A component
update arrives as a new snapshot commit on `main`, and nothing in Lore returns to
GitHub.

The Gateway issues Lore tokens (D43). `vv-lore-tokens` keeps each environment's
`/run/lore/token` current with a 15-minute token for that environment's Lore client,
which reaches only its component's repository. The file belongs to root and the
`lore-cred` group, and only the setgid `lore` client reads it. The client sends the
token only to `vv-lore.internal`. `main` is protected in every repository, so an
environment pushes branches, and the Lore admin client, a Lore service account,
merges.

## Isolated Coding Environments

Complete the trusted installation below first. Keep its existing state volumes private;
source for agents is cloned anew from Lore. The dev containers are `vv-dev-gateway`,
`vv-dev-time`, `vv-dev-artifact` and `vv-dev-media`. `vv-review` is trusted Lore admin
transport: do not execute repository code there. Review and test in dev before merging.

1. `autonomy/component-lock.json` pins the Gateway revision used by the trusted SDS
   refresher separately from the deployed runtime snapshot. With that revision present
   in the sibling Gateway checkout, build its own `runtime` stage. Build the component
   `dev` images and Lore as described below, then run:

   ```sh
   gateway_revision=$(jq -er '.components[] | select(.name == "veoveo-service-gateway") | .revision' autonomy/component-lock.json)
   git -C ../veoveo-service-gateway archive "$gateway_revision" \
     | docker build --target runtime -t veoveo-service-gateway:autonomy-runtime -
   docker compose --profile autonomy build vv-dev-gateway vv-dev-time vv-dev-artifact vv-dev-media
   python3 autonomy/provision
   docker compose --profile autonomy up -d vv-autonomy-tokens
   docker compose --profile autonomy up -d vv-autonomy-edge vv-review vv-dev-gateway vv-dev-time vv-dev-artifact vv-dev-media
   ```

   Provisioning reads `HF_TOKEN` from the ignored `.env`, sends it through stdin to
   the edge-only volume and generates a TLS leaf from the existing installation CA.
   It never prints the credential or puts it in a command argument. Envoy must be
   restarted after replacing the inference key. Lore SDS tokens rotate automatically.
   Keep `.env` owner-readable (`chmod 600 .env`); Git and Docker ignore it.

2. Clone the component in each dev container, substituting its name:

   ```sh
   docker compose exec vv-dev-time lore -P clone grpcs://lore-proxy.internal:7443/veoveo-mcp-time /sandbox/src
   docker compose exec -w /sandbox/src vv-dev-time sh -c 'test -f .loreignore || cp /etc/opencode/loreignore .loreignore'
   docker compose exec -w /sandbox/src vv-dev-time lore -P status
   docker compose exec -w /sandbox/src vv-dev-time opencode
   ```

   OpenCode 2.0.29 is pinned by npm package integrity for ARM64 and AMD64. Its managed
   config selects `XiaomiMiMo/MiMo-V2.6-Pro-RL:novita` through
   `https://inference.internal:8443/v1`. Only a public placeholder is in the process
   environment. Automatic updates and Git snapshots are disabled; Lore checkpoints
   and branches are the version history. For a bounded, logged headless task:

   ```sh
   docker compose exec -T -w /sandbox/src vv-dev-time timeout --kill-after=30s 1200 \
     opencode run --standalone --auto --format json 'Implement the requested change on a Lore task branch, test it, and commit it. Await independent review before pushing.'
   ```

3. Review the branch and run the component's checks before accepting it. Use
   `vv-review` only for Lore clone, inspection and merge commands. Dev credentials
   cannot update protected `main`; the trusted reviewer can. Merging source does not
   deploy it. Build and promote an approved runtime separately; never point a running
   credential-bearing service at an agent's writable binary or source directory.

Each dev network is internal, has one fixed dev peer and one Envoy peer, and carries
no runtime service. Lore listener selection and RBAC use that actual network peer;
`Authorization`, `Host` and forwarded-address headers cannot select another client.
The review network has its own admin listener. TLS is verified on both Lore hops.
Inference permits only POST `/v1/chat/completions` to the fixed Hugging Face host;
Envoy replaces authorization and verifies upstream TLS. The dependency proxy permits
only the listed Rust/crates.io/GitHub hosts. Envoy's admin interface is loopback-only.
No dev container mounts a token volume, host directory, runtime state or Docker socket.
These OS/network boundaries protect credentials even if an agent changes its own code
or configuration. Model access remains a billed capability; use bounded tasks.

The initial migration backup is a private named volume, never a dev mount. To repair
an existing stale Time branch pointer, first preserve its `.lore` directory, verify
working files match the intended remote revision, then use `lore branch reset REV
--branch main`, `lore sync`, and `lore repository verify`. No Lore algorithm changes
are needed for this repair.

## Local Installation

Requirements: Docker with Compose 2.24 or newer, `jq` and `openssl`. On macOS, Docker
Desktop 4.94 or newer. Run every step from this repository's directory. Every image and
every Lore repository comes from the revision `component-lock.json` names; the helper
below reads it:

```sh
rev() { jq -er --arg name "$1" '.components[] | select(.name == $name) | .revision' component-lock.json; }
```

1. Keep `VEOVEO_POSTGRES_PASSWORD` (the superuser's), `VEOVEO_DATABASE_PASSWORD` (the
   installation owner's), `VEOVEO_STORAGE_ACCESS_KEY` and `VEOVEO_STORAGE_SECRET_KEY`
   (the object store's credential), `VEOVEO_SEAWEEDFS_ADMIN_PASSWORD` (the password of
   SeaweedFS's admin UI) and, optionally, `VEOVEO_DATABASE_PORT` (5432 by default),
   `VEOVEO_STORAGE_PORT` (9000 by default) and `VEOVEO_SEAWEEDFS_ADMIN_PORT` (23646 by
   default) in an uncommitted `.env` file next to `compose.yaml`. The commands below
   write new credentials, generate an admin password when `.env` has none, and keep
   every other setting in `.env`, such as those of the [public origin](#public-origin)
   and the [real media provider](#real-media-provider). Then they render the edge's
   configuration and create the installation CA with certificates for Lore and the
   provider route:

   ```sh
   umask 077
   touch .env
   sed -E '/^VEOVEO_(POSTGRES_PASSWORD|DATABASE_PASSWORD|STORAGE_ACCESS_KEY|STORAGE_SECRET_KEY)=/d' .env > .env.next
   printf 'VEOVEO_POSTGRES_PASSWORD=%s\nVEOVEO_DATABASE_PASSWORD=%s\nVEOVEO_STORAGE_ACCESS_KEY=%s\nVEOVEO_STORAGE_SECRET_KEY=%s\n' \
     "$(openssl rand -hex 24)" "$(openssl rand -hex 24)" "$(openssl rand -hex 12)" "$(openssl rand -hex 24)" >> .env.next
   grep -q '^VEOVEO_SEAWEEDFS_ADMIN_PASSWORD=' .env.next \
     || printf 'VEOVEO_SEAWEEDFS_ADMIN_PASSWORD=%s\n' "$(openssl rand -hex 12)" >> .env.next
   mv .env.next .env
   ./egress/render
   mkdir -p tls/ca tls/private tls/lore tls/egress
   openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -days 825 \
     -subj "/CN=Veoveo local installation CA" -keyout tls/private/ca.key -out tls/ca/ca.crt \
     -addext basicConstraints=critical,CA:TRUE -addext keyUsage=critical,keyCertSign,cRLSign
   for name in lore/vv-lore.internal egress/media-provider.internal; do
     host=${name#*/}
     openssl req -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -subj "/CN=$host" \
       -keyout "tls/$name.key" -out "tls/private/$host.csr"
     printf 'subjectAltName=DNS:%s\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature\nextendedKeyUsage=serverAuth\n' "$host" \
       > "tls/private/$host.ext"
     openssl x509 -req -in "tls/private/$host.csr" -CA tls/ca/ca.crt -CAkey tls/private/ca.key \
       -CAcreateserial -days 825 -extfile "tls/private/$host.ext" -out "tls/$name.crt"
   done
   ```

2. Build the images. Each component's `dev` image comes from its repository at its
   locked revision, the Gateway's `runtime` image runs the Lore token service, and
   Compose builds Lore and the installation's layer over each `dev` image:

   ```sh
   for c in veoveo-service-gateway veoveo-mcp-time veoveo-mcp-artifact veoveo-mcp-media; do
     docker build --target dev -t "$c:dev" "https://github.com/VeoveoAI/$c.git#$(rev $c)"
   done
   docker build --target runtime -t veoveo-service-gateway:runtime \
     "https://github.com/VeoveoAI/veoveo-service-gateway.git#$(rev veoveo-service-gateway)"
   docker compose --profile envs build vv-lore
   docker compose --profile envs build
   ```

3. Give the edge placeholder secrets and start PostgreSQL, SeaweedFS and the edge:

   ```sh
   docker run --rm --entrypoint sh -v vv-local_vv-egress-secrets:/secrets vv-lore:local -c \
     'umask 077 && for s in registration-secret media-provider-key; do [ -e /secrets/$s ] || printf "Bearer unset" > /secrets/$s; done'
   docker compose up -d --wait
   ```

4. Start the Gateway environment. Its first source is its locked GitHub snapshot,
   because Lore starts only once the Gateway serves its keys; step 5 moves it to Lore.
   Give it the installation owner's password, and only that one, then generate the
   installation once with a Lore client for each environment:

   ```sh
   docker compose --profile envs up -d vv-srv-gateway
   docker compose exec vv-srv-gateway bash -c "git clone --quiet https://github.com/VeoveoAI/veoveo-service-gateway /sandbox/src \
     && git -C /sandbox/src checkout --quiet --detach $(rev veoveo-service-gateway)"
   grep '^VEOVEO_DATABASE_PASSWORD=' .env | docker compose exec -T vv-srv-gateway sh -c \
     'mkdir -p /sandbox/state/gateway && umask 077 && cat > /sandbox/state/database.env'
   docker compose exec vv-srv-gateway bash -lc 'cd /sandbox/src \
     && cargo build --locked --target-dir /sandbox/target-serve --bin veoveo-service-gateway \
     && /sandbox/target-serve/debug/veoveo-service-gateway generate-local-installation \
          --directory /sandbox/state/gateway --issuer http://vv-gateway.internal:8080 \
          --lore-resource lores://vv-lore.internal:41337 \
          --lore-environment vv-srv-gateway --lore-environment vv-mcp-time \
          --lore-environment vv-mcp-artifact --lore-environment vv-mcp-media'
   ```

   The generated configuration has no policy rules. The installation lets
   `acceptance-admin` make administrative reads, such as the cost views and server
   health, with one rule. The edge then takes the registration secret without printing
   it:

   ```sh
   docker compose exec -T vv-srv-gateway cat /sandbox/state/gateway/gateway.json \
     | jq '.policies[0].rules = [{id: "administrative-reads", effect: "allow", actions: ["admin_read"],
             principalIds: [.authorizationServers[0].issuer + "#acceptance-admin"]}]' \
     | docker compose exec -T vv-srv-gateway sh -c 'cat > /sandbox/state/gateway/gateway.json.next \
         && mv /sandbox/state/gateway/gateway.json.next /sandbox/state/gateway/gateway.json'
   docker compose exec -T vv-srv-gateway bash -c '. /sandbox/state/gateway/gateway.env && printf "Bearer %s" "$VEOVEO_REGISTRATION_SECRET"' \
     | docker run --rm -i --entrypoint sh -v vv-local_vv-egress-secrets:/secrets vv-lore:local -c \
         'umask 077 && cat > /secrets/registration-secret'
   docker compose restart vv-egress
   ```

   Then start the Gateway in its own terminal, as its README's Local Launch section
   shows.

5. Start Lore and create each component's repository from its locked snapshot as the
   Lore admin. The admin protects `main` in each, and its output names each repository's
   ID:

   ```sh
   docker compose --profile envs up -d vv-lore vv-lore-tokens vv-lore-admin
   until docker compose exec vv-lore-admin lore repository list lores://vv-lore.internal:41337 >/dev/null 2>&1; do sleep 2; done
   for c in $(jq -r '.components[].name' component-lock.json); do
     docker compose exec -T vv-lore-admin bash -ec "
       git clone --quiet https://github.com/VeoveoAI/$c /sandbox/git/$c
       git -C /sandbox/git/$c checkout --quiet --detach $(rev $c)
       mkdir -p /sandbox/lore/$c && git -C /sandbox/git/$c archive HEAD | tar -x -C /sandbox/lore/$c
       cd /sandbox/lore/$c
       lore repository create lores://vv-lore.internal:41337/$c | sed -n 's/.* with ID \([0-9a-f]*\)$/\1/p' > /sandbox/lore/$c.id
       lore dirty . >/dev/null && lore stage . >/dev/null
       lore commit '$c $(rev $c)' >/dev/null && lore push >/dev/null && lore branch protect main >/dev/null"
   done
   ```

   Grant each environment its component's repository, restart the Gateway as step 4
   started it, and refresh the tokens:

   ```sh
   ids=$(for pair in vv-srv-gateway:veoveo-service-gateway vv-mcp-time:veoveo-mcp-time \
         vv-mcp-artifact:veoveo-mcp-artifact vv-mcp-media:veoveo-mcp-media; do
     printf '{"client":"lore-%s","id":"%s"}\n' "${pair%%:*}" \
       "$(docker compose exec -T vv-lore-admin cat /sandbox/lore/${pair#*:}.id)"
   done | jq -s .)
   docker compose exec -T vv-srv-gateway cat /sandbox/state/gateway/gateway.json \
     | jq --argjson ids "$ids" '.lore.grants |= map(.client as $c
         | ($ids | map(select(.client == $c)) | first) as $grant
         | if $grant then .repositories = [$grant.id] else . end)' \
     | docker compose exec -T vv-srv-gateway sh -c 'cat > /sandbox/state/gateway/gateway.json.next \
         && mv /sandbox/state/gateway/gateway.json.next /sandbox/state/gateway/gateway.json'
   docker compose exec vv-srv-gateway pkill -TERM -f '^/sandbox/target-serve/debug/veoveo-service-gateway serve'
   ```

   After the Gateway runs again:

   ```sh
   docker compose restart vv-lore-tokens
   docker compose exec vv-srv-gateway bash -c 'mv /sandbox/src /sandbox/src-github \
     && lore clone lores://vv-lore.internal:41337/veoveo-service-gateway /sandbox/src \
     && rm -rf /sandbox/src-github'
   ```

   The Gateway environment now works in Lore. The running Gateway was built from the
   same files.

6. Start the Time environment, clone Time from Lore, then start Time in its own
   terminal as its README shows. Time registers itself with the Gateway at startup:

   ```sh
   docker compose --profile envs up -d vv-mcp-time
   docker compose exec vv-mcp-time lore clone lores://vv-lore.internal:41337/veoveo-mcp-time /sandbox/src
   ```

7. Start the Artifact environment and clone Artifact. Artifact signs transfers with the
   object store's credential itself, so it receives that credential, and only that one,
   as an owner-only file:

   ```sh
   docker compose --profile envs up -d vv-mcp-artifact
   docker compose exec vv-mcp-artifact lore clone lores://vv-lore.internal:41337/veoveo-mcp-artifact /sandbox/src
   grep -E '^VEOVEO_STORAGE_(ACCESS|SECRET)_KEY=' .env | docker compose exec -T vv-mcp-artifact sh -c \
     'mkdir -p /sandbox/state && umask 077 && cat > /sandbox/state/storage.env'
   ```

   Then start Artifact in its own terminal, as its README's Running Artifact section
   shows. Artifact prepares its bucket and registers itself with the Gateway at startup.
   With a [public origin](#public-origin), start it with `VEOVEO_PUBLIC_ORIGIN` set to
   that origin, so share links name it.

8. Start the Media environment and clone Media. The local installation runs Media
   against its fake provider, which shares a webhook secret with Media. Both values live
   in an owner-only file the environment generates:

   ```sh
   docker compose --profile envs up -d vv-mcp-media
   docker compose exec vv-mcp-media lore clone lores://vv-lore.internal:41337/veoveo-mcp-media /sandbox/src
   docker compose exec vv-mcp-media bash -c 'mkdir -p /sandbox/state && umask 077 \
     && printf "MEDIA_PROVIDER_API_KEY=fake\nMEDIA_PROVIDER_WEBHOOK_SECRET=whsec_%s\n" \
          "$(head -c 24 /dev/urandom | od -An -tx1 | tr -d " \n")" > /sandbox/state/media.env'
   ```

   Then start the fake provider on `127.0.0.1:8803` and Media in their own terminals, as
   its README's Running Media section shows. Media registers itself with the Gateway at
   startup. Without a public origin, runs complete through status checks of the fake.
   With a [public origin](#public-origin), start Media with `VEOVEO_PUBLIC_ORIGIN` set to
   that origin; the fake provider then posts each outcome through the tunnel to Media's
   callback route. [Real Media Provider](#real-media-provider) runs Media against the
   provider itself.

9. To run the acceptance tests of Time, Artifact and Media, copy the callers' keys from
   the Gateway environment into `/sandbox/acceptance` in each environment and follow the
   Acceptance section of each README:

   ```sh
   for env in vv-mcp-time vv-mcp-artifact vv-mcp-media; do
     docker compose exec -T vv-srv-gateway tar -C /sandbox/state/gateway -cf - \
         acceptance-member.pem acceptance-member.jwks.json acceptance-admin.pem acceptance-admin.jwks.json \
       | docker compose exec -T $env sh -c 'mkdir -p /sandbox/acceptance && chmod 700 /sandbox/acceptance \
           && tar -C /sandbox/acceptance -xf - && chmod 600 /sandbox/acceptance/*.pem'
   done
   ```

10. To call the installation from the host, install the SDK's
    [Gateway client](https://github.com/VeoveoAI/veoveo-sdk-rust/blob/e8b2dcc88985f29fc82f5b5c634d24f3142577c5/crates/veoveo-sdk-rust-cli/DESIGN.md)
    and copy the callers' keys into `state/callers`, which Git ignores:

    ```sh
    cargo install --locked --git https://github.com/VeoveoAI/veoveo-sdk-rust \
      --rev e8b2dcc88985f29fc82f5b5c634d24f3142577c5 veoveo-sdk-rust-cli
    mkdir -p state/callers && chmod 700 state/callers
    docker compose exec -T vv-srv-gateway tar -C /sandbox/state/gateway -cf - \
        acceptance-member.pem acceptance-member.jwks.json acceptance-admin.pem acceptance-admin.jwks.json \
      | tar -C state/callers -xf - && chmod 600 state/callers/*.pem
    veoveo-sdk-rust-cli --connect 127.0.0.1:8080 --keys state/callers tools
    ```

    The client reaches the Gateway through the edge's published port, and its tokens
    still name `vv-gateway.internal`. Its `ask` command lets a chat model work with the
    caller's tools, and it reads the model endpoint's token from `HF_TOKEN` in `.env`:

    ```sh
    veoveo-sdk-rust-cli --connect 127.0.0.1:8080 --keys state/callers --caller acceptance-admin \
      ask --env-file .env "Generate an image of a red circle with the fake text-to-image model."
    ```

Names follow the Veoveo
[naming and format conventions](https://github.com/VeoveoAI/veoveo-core/blob/main/docs/CONVENTIONS.md).

## Working In Lore

An environment edits its working copy at `/sandbox/src` and pushes its own branch:

```sh
docker compose exec vv-mcp-time bash -c 'cd /sandbox/src \
  && lore branch create agent/fix-schedule && lore dirty . && lore stage . \
  && lore commit "Fix the schedule Task" && lore push'
```

The Lore admin merges a branch into `main` from its own working copy of the repository
and pushes it. A merge with conflicts stops for `lore branch merge resolve` after the
admin settles each file:

```sh
docker compose exec vv-lore-admin bash -c 'cd /sandbox/lore/veoveo-mcp-time \
  && lore sync main@LATEST && lore branch merge agent/fix-schedule && lore push'
```

To move a component to a new revision, change it in `component-lock.json`, commit, and
record its snapshot in Lore as a new commit on `main`:

```sh
c=veoveo-mcp-time
docker compose exec -T vv-lore-admin bash -ec "
  git -C /sandbox/git/$c fetch --quiet && git -C /sandbox/git/$c checkout --quiet --detach $(rev $c)
  cd /sandbox/lore/$c && lore sync main@LATEST >/dev/null
  find . -mindepth 1 -maxdepth 1 ! -name .lore -exec rm -rf {} +
  git -C /sandbox/git/$c archive HEAD | tar -x -C /sandbox/lore/$c
  lore dirty . >/dev/null && lore stage . >/dev/null
  lore commit '$c $(rev $c)' >/dev/null && lore push >/dev/null"
```

The environment then runs `lore sync main@LATEST` in `/sandbox/src`, and its component restarts
as its README shows. A new `dev` image, from step 2, needs the environment recreated:
stop the component, run `docker compose --profile envs up -d --build`, and start the
component again. `/sandbox` is the environment's volume, so its working copy, builds and
state stay: the Gateway's configuration, secrets and callers' keys in `/sandbox/state`,
and the key each server's namespace is pinned to. Registered servers stay registered.

## Public Origin

An installation has one public origin, an `https` origin without a path such as
`https://veoveo.example.com`, and serves each public route under its own path. The local
installation publishes the two routes that callers without an account use: the media
provider's callbacks under `/media/operations/` and Artifact's share links under
`/artifact/shares/`.

The optional `tunnel` Compose profile connects the origin to the workstation through a
remote-managed [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/).
Create the tunnel with a proxied DNS record for the origin's host and these ingress
rules, in this order:

| Path | Service |
|---|---|
| `^/media/operations/` | `http://127.0.0.1:8802` |
| `^/artifact/shares/` | `http://127.0.0.1:8801` |
| Any other | `http_status:404` |

Add the origin as `VEOVEO_PUBLIC_ORIGIN` and the tunnel's connector token as
`VEOVEO_TUNNEL_TOKEN` to `.env`. The edge's proxy then admits the origin's host, which
Artifact's acceptance tests and the fake provider reach from their environments.
Render the edge again and start the tunnel:

```sh
./egress/render
docker compose restart vv-egress
docker compose --profile tunnel up -d vv-tunnel
```

Artifact and Media start with `VEOVEO_PUBLIC_ORIGIN` set to the origin and accept
requests for its host. Artifact's share links name the origin, and the provider posts
each run's outcome to Media's callback route under it.

## Real Media Provider

Media runs against its fake provider by default. A run against the media provider itself
bills the provider's account. Keep the provider's API URL as `MEDIA_PROVIDER_URL` and the
hosts its outputs come from as `MEDIA_OUTPUT_HOSTS`, separated by commas, in `.env`, and
the account's API key and webhook secret in `MEDIA_PROVIDER_API_KEY` and
`MEDIA_PROVIDER_WEBHOOK_SECRET` in the shell's environment.

The edge holds the API key and adds it to every request Media sends to
`media-provider.internal`, which only Media's network reaches. Render the edge with the
provider's hosts and give it the key without printing it:

```sh
./egress/render
printf 'Bearer %s' "$MEDIA_PROVIDER_API_KEY" \
  | docker run --rm -i --entrypoint sh -v vv-local_vv-egress-secrets:/secrets vv-lore:local -c \
      'umask 077 && cat > /secrets/media-provider-key'
docker compose restart vv-egress
```

Media checks the provider's webhook signatures itself, so it receives the webhook secret
as an owner-only file:

```sh
printf 'MEDIA_PROVIDER_WEBHOOK_SECRET=%s\n' "$MEDIA_PROVIDER_WEBHOOK_SECRET" \
  | docker compose exec -T vv-mcp-media sh -c 'umask 077 && cat > /sandbox/state/media-provider.env'
```

Stop Media and the fake provider as [Stop](#stop) shows, then start Media against the
provider through the edge, with the path of `MEDIA_PROVIDER_URL` after the edge's name.
Media receives the API key's placeholder, which the edge replaces:

```sh
origin=$(sed -n 's/^VEOVEO_PUBLIC_ORIGIN=//p' .env)
provider=$(sed -n 's#^MEDIA_PROVIDER_URL=https://[^/]*##p' .env)
outputs=$(sed -n 's/^MEDIA_OUTPUT_HOSTS=//p' .env)
docker compose exec vv-mcp-media env ${origin:+VEOVEO_PUBLIC_ORIGIN=$origin} \
    MEDIA_PROVIDER_URL="https://media-provider.internal$provider" MEDIA_OUTPUT_HOSTS="$outputs" \
    MEDIA_PROVIDER_API_KEY=replaced-by-the-edge \
  bash -lc 'cd /sandbox/src \
  && cargo build --locked --target-dir /sandbox/target-serve --bin veoveo-mcp-media \
  && set -a && . /sandbox/state/media-provider.env && set +a \
  && VEOVEO_PUBLIC_BASE_URL=http://vv-mcp-media.internal:8802 \
     VEOVEO_GATEWAY_ISSUER=http://vv-gateway.internal:8080 \
     VEOVEO_KEY_DIRECTORY=/sandbox/media/keys \
     /sandbox/target-serve/debug/veoveo-mcp-media'
```

Media's acceptance tests run the fake provider's model, so they run with the fake
provider. Media's README's Provider Qualification section runs one billed generation
through the whole flow.

To return to the fake provider, stop Media, give the edge the placeholder key again and
remove the webhook secret, then start the fake provider and Media as step 8 shows:

```sh
docker compose exec vv-mcp-media pkill -TERM -f '^/sandbox/target-serve/debug/veoveo-mcp-media'
docker run --rm --entrypoint sh -v vv-local_vv-egress-secrets:/secrets vv-lore:local -c \
  'umask 077 && printf "Bearer unset" > /secrets/media-provider-key'
docker compose restart vv-egress
docker compose exec vv-mcp-media rm -f /sandbox/state/media-provider.env
```

## Stop

Stop each service with Ctrl-C in its terminal, or from the host, then stop the
containers. The data stays in the Compose volumes, and the steps above start the
installation again:

```sh
docker compose exec vv-mcp-media pkill -TERM -f '^/sandbox/target-serve/debug/veoveo-mcp-media'
docker compose exec vv-mcp-artifact pkill -TERM -f '^/sandbox/target-serve/debug/veoveo-mcp-artifact'
docker compose exec vv-mcp-time pkill -TERM -f '^/sandbox/target-serve/debug/veoveo-mcp-time'
docker compose exec vv-srv-gateway pkill -TERM -f '^/sandbox/target-serve/debug/veoveo-service-gateway'
docker compose --profile envs --profile tunnel stop
```

The first command stops Media and its fake provider. Time, Artifact and Media remove
their registrations when they receive SIGTERM.

## Reset

A server's key lives in its environment, and the Gateway pins a namespace to the first
key that registers it. A recreated environment has a new key, so its server needs a
fresh namespace claim, which a reset of the database provides. After the steps in Stop,
remove the containers and every volume, then start again from step 1. Compose reads
every variable `compose.yaml` requires even to remove the services, so an `.env` that
holds no object store credential or admin password gets placeholders first; step 1
writes new credentials and keeps the admin password:

```sh
grep -q '^VEOVEO_STORAGE_SECRET_KEY=' .env || printf 'VEOVEO_STORAGE_ACCESS_KEY=reset\nVEOVEO_STORAGE_SECRET_KEY=reset\n' >> .env
grep -q '^VEOVEO_SEAWEEDFS_ADMIN_PASSWORD=' .env || printf 'VEOVEO_SEAWEEDFS_ADMIN_PASSWORD=reset\n' >> .env
docker compose --profile envs --profile tunnel down -v --remove-orphans
rm -rf tls
```

## License

Apache-2.0. See [LICENSE](LICENSE).
