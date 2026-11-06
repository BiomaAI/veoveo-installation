# Bioma's selections

This repository follows [veoveo-template-installation](https://github.com/VeoveoAI/veoveo-template-installation)
at `51f2c7bd51e9d708a91b56e6f36ca56073302fa4`, the template's `cleanup` branch over its
main `67b7032e988a71d80938c4e4e79897f78c3a8152`. The shared files carry Bioma's
values in place of the template's placeholders, and [DESIGN.md](../../DESIGN.md) is the
template's, verbatim. Its installer (`installer/`) and its declaration (`installation.toml`)
follow the template's `template-release-note` branch at
`87cb6bf597a0404cc89079220244b8d16c722ecd`; [DESIGN.md](../../DESIGN.md), Lore's
settings and Deployment (`kubernetes/lore.toml`, `lore.yaml`), `openshell.values.yaml`'s
chart revision and `service.clusterIP`, and the Lore paragraphs of `WORKLOADS.md` and
the chart paragraph of `kubernetes/README.md` follow its `lore-catalog` branch at
`ce9e4bc9eda890a9b872d6a5ea5b1e93decfcdd6`, which includes that revision. This page lists
what Bioma selected and every other place where a file differs from the template.

## Placement

- One Linux amd64 node (Ubuntu 24.04.5) running K3s `v1.36.5+k3s1`.
- [cilium-node.values.yaml](kubernetes/cilium-node.values.yaml) holds the node's API
  address. It is the template's private Cilium node override (`[helm.cilium]` in
  `private.toml`, in the
  [foundation steps](../../kubernetes/README.md#cluster-and-controllers)), which
  Bioma keeps here and `installation.toml` names.
- The operator's private directory on the node is
  `~/.config/veoveo/k3s/private/bioma`, mode `0700`, the installer's `--private`.
  It holds `private.toml` and the private inputs the guides name; it is a path, not a
  secret, and nothing in it enters this repository.
- The OpenShell gateway ID is `openshell`. The workspaces are `vv-control` (Hub),
  `vv-services` (MCP servers), `vv-factory` (factory sandboxes) and `installation`
  (the Computer and factory templates). Their managed namespaces are
  `openshell-openshell-<workspace>`, the names the builder's and log store's network
  policies use.
- The embedding runtime uses the node's GPU through the NVIDIA device plugin.
- The gateway Service's cluster IP is `10.43.227.28`, the address Kubernetes gave it
  when it was created. `openshell.values.yaml` declares it as `service.clusterIP`, and
  `lore.yaml`'s host alias names it so that Lore reaches Hub's service route for
  repository listings.

## Public host and tunnel

- Hub's public origin is `https://veoveo.bioma.ai`. Signed objects are served under
  `/artifacts/` on that host.
- The tunnel is Bioma's existing remotely managed Cloudflare tunnel. Its routes live
  in Cloudflare. [tunnel-routes.yaml](../../kubernetes/tunnel-routes.yaml) records
  them for the Bioma host. The routes held in Cloudflare were read back for this
  revision, at the tunnel's version 12.
- The content domain is `veoveo-bioma.space`, another registrable domain from Hub's, so
  a browser sends none of Hub's or an App's cookies there. Its wildcard route goes to
  Hub's `apps` service, set through the API, and its zone bypasses the edge cache and
  rewrites nothing. `installation.toml` sets it as Hub's `VEOVEO_CONTENT_ORIGIN`.
- `/docs/` on the same host is served at Cloudflare's edge by the veoveo-docs Worker,
  public by the owner's choice; [edge-routes.yaml](../../kubernetes/edge-routes.yaml)
  records its Workers route. It never reaches the tunnel or Hub.

## Identity

| Identity | Value |
|---|---|
| Entra tenant | `e0ee3c6a-4f58-4f66-8de4-253226eeed5f` |
| Hub's Entra broker application (confidential Web app, `/oauth/callback`), the `entra` client | `853550a7-5fd4-421c-abd2-bea0216fa579` |
| OpenShell gateway resource application (gateway OIDC audience) | `8a6d434f-8c4c-4e2c-9756-9b2d94118d17` |
| Gateway app roles, in the `roles` claim | `openshell-admin`, `openshell-user` |
| Hub access-token signing key ID | `nr-CyVKgU-7yqss1O9KW-8gr4WMw8a1JWOupDeCieFc` |
| Hub installation names | the template's: tenant `reference`, policy revision `reference-policy` |

Principal object IDs, grants, groups, repository registrations and assignments are
per-person data. They are not in this repository.
[entra.example.json](../../identity/entra.example.json) keeps the template's
example principals.

## Services

- Hub, plus Artifact, Media, Embedding and console in `vv-services`.
- Media runs against the synthetic fake provider (the `media-provider` image in
  [component-lock.json](../../component-lock.json)). It does no real media
  generation and checks run status; the tunnel holds its callback route all the same, as
  [tunnel-routes.yaml](../../kubernetes/tunnel-routes.yaml) records.
- Time is not an installed service.
- USD is not an installed service. It runs as a factory instance from its own Lore repository,
  `veoveo-mcp-usd`, whose image opts in to the GPU, and the Lore repository `usd-demo` holds its scenes.
- Thumb and Repo are not installed services either. Each runs as a factory instance from its own Lore repository: `veoveo-mcp-thumb`,
  whose image opts in to the GPU, and `veoveo-mcp-repo`.
- Computers use the template's DeepInfra model provider.
- Hub's `computers.skills` are the template's
  [computer/skills/](../../computer/skills/).
- `computer-v1`'s `release_note` in `installation.toml` is the template's; `factory-v1` carries none.

## Not yet deployed

The running Lore server's `lore-settings` is [lore.toml](../../kubernetes/lore.toml) as
`main` holds it, byte for byte, with no hook (SHA-256 `c2da31c4…`, read on 2026-10-26
UTC).

On the `lore-catalog` branch, `lore.toml`, `lore.yaml` and `openshell.values.yaml` are
ahead as well. Lore's repository listing asks Hub, which answers
`UrcAuthApi.LookupUserPermissions` from Hub's `lore-catalog` branch at `2faa2d2`: apply
Lore's files after Hub runs that revision; before it, `lore repository list` fails while
every other Lore request works. The `openshell` step needs the chart's checkout at
OpenShell `ebd6a1c` (identical to `c80bda201` there), which reads `service.clusterIP`; the declared address is the
Service's own, so the upgrade changes no live address.

## Deployed revisions

[component-lock.json](../../component-lock.json) names each Veoveo component's revision
and every image Bioma built, by the digest the cluster runs, updated at each
deployment. Core's component-lock format holds one revision per Veoveo repository and no
other repository, so these provenances are here:

| Image | Built from |
|---|---|
| `openshell-gateway`, `openshell-supervisor` | OpenShell `8bd83351d776127fcd619fb9329ecc9e41873016`: strict credential binding, delivered apart from credential values, and HTTP/2 upstream only when the upstream selects it. The gateway runs it since 07:15 UTC on 2026-10-31; a sandbox takes the supervisor when it is next created: a factory instance at a push that changes its image, policy or providers, a Computer at its restart |
| `openshell-sandbox` | OpenShell `1ab0e2386cbd943ec84a8701cd5d54dfa68e55a7` |
| `lore` | Lore `c33e017a`, with the template's Lore Dockerfile. Hub, the factory sandboxes and the Computer run this digest |
| `lore-server` | Lore `2c0c689bbfc9239ddb4ad01f751f27ce9f518019`, which serves its HTTP port over TLS and answers a Range on a file's content, with the template's Lore Dockerfile, published as `veoveo/lore:2c0c689b`. Only the Lore server runs this digest |
| `file-viewer` | `@file-viewer/web-full` 3.3.3 and its assets, unmodified, with [FileViewer.Dockerfile](../../factory/FileViewer.Dockerfile). Only Hub mounts it. Its own source is Apache-2.0, its DWG, DWF and DWFx engine AGPL-3.0-only and its LibreDWG bindings GPL-3.0-only; their notices and source link stay in the image |
| `computer` | The template at `9f21d3e` over the `factory` image, with OpenCode `c5fb62662c9c6fcb5064ef191956ca0da14e1af9`; the current template's Computer build inputs are the same |
| `factory` | The template at `9f21d3e`, the base of the `computer` image; no workload runs it directly |
| `media-provider` | Media `6a73e52932d166e368ba8673277cadf8be1742b9`, target `fake-provider`; the lock's Media revision is the server's, `6bd5843` |
| `postgres` | The template at `ecdb5b5dcc621161c7e5905a243c1271b42daeff` |
| `hub-sdk-cli` | The SDK at `05273d1`, target `cli` |

The lock's revisions are Bioma's own, not the template's. Its `veoveo-template-installation`
revision is the template's main that these files last took, and the images above name
their own template revision. Its `veoveo-hub-sdk` revision is the one the deployed Hub
pins; other servers pin their own.

## Differences from the template

Besides placeholder values, these files differ from the template:

| File | Difference | Reason |
|---|---|---|
| `component-lock.json` | Names Bioma's deployed revisions and images, the template's own revision, and no Time | The lock is what Bioma runs. Time is not installed |
| `installation.toml` | Cilium's values add `openshell/bioma/kubernetes/cilium-node.values.yaml` | Bioma keeps its node override in this repository |
| `component-lock.json`, `kubernetes/lore.yaml`, `installer/tests/repository.rs` | The Lore server runs its own image, `@image:lore-server@`, which the installer's test lock names too | `lore` is mounted in Computers and factories, so a new digest there would change their templates. The server's change is to its HTTP files only, and gRPC is the same |
| `kubernetes/hub-config-pvc.yaml`, `media-provider-config-pvc.yaml`, `postgres-client-ca.yaml`, `seed-service-configs.yaml` | The copy-image markers name the pinned `debian:trixie-slim` copy utility | These values are rendered here; the utility is third-party, pinned at its upstream registry, so the lock does not name it |
| Comments and sentences that say to render the host, image or gateway ID (`kubernetes/README.md`, `WORKLOADS.md`, `lore.toml`, `openshell.values.yaml`, `embedding-storage.yaml`, `postgres.yaml`, `seed-service-configs.yaml`, `tunnel-routes.yaml`, `policies/console.yaml`, `policies/factory-base.yaml`, `openshell/providers/factory-lore.yaml`, `factory-registration.yaml`, `lore.yaml`) | Reworded | These values are already rendered here |
| `README.md`, `AGENTS.md` | Describe this repository | Bioma's repository, not the template |
| Links to template files left out of this repository | Point to the template at `51f2c7b` | These files are the template's Mac and Docker fixtures and its Docker-era reference documents |

`lore.yaml`, `postgres.yaml` and the Hub, Computer and factory driver configurations
keep the template's `@image:<name>@` placeholders, which the installer fills from the
lock, as the template's
[naming each image once](../../kubernetes/README.md#naming-each-image-once) says.

The template files left out are its Mac and Docker development fixtures: Compose,
local Keycloak and Envoy, the Docker gateway configuration, policies and mounts, the
Docker Lore configuration, the Docker variants of the Computer files, and the
Docker-era `openshell/` documents. Time's registration profile,
`openshell/providers/time-registration.yaml`, is left out too, because Time is not
installed.
