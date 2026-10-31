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
  them for the Bioma host. The routes held in Cloudflare were not read back for this
  revision, because that needs the operator's API credential.

## Identity

| Identity | Value |
|---|---|
| Entra tenant | `e0ee3c6a-4f58-4f66-8de4-253226eeed5f` |
| Hub's Entra broker application (confidential Web app, `/oauth/callback`), the `entra` client | `853550a7-5fd4-421c-abd2-bea0216fa579` |
| OpenShell gateway resource application (gateway OIDC audience) | `8a6d434f-8c4c-4e2c-9756-9b2d94118d17` |
| Gateway app roles, in the `roles` claim | `openshell-admin`, `openshell-user` |
| Hub access-token signing key ID | `nr-CyVKgU-7yqss1O9KW-8gr4WMw8a1JWOupDeCieFc` |
| Hub installation names | the template's: tenant `reference`, Work Context `reference-work`, policy revision `reference-policy` |

Principal object IDs, grants, Work Context memberships, repository registrations and
assignments are per-person data. They are not in this repository.
[entra.example.json](../../identity/entra.example.json) keeps the template's
example principals.

## Services

- Hub, plus Artifact, Media, Embedding and console in `vv-services`.
- Media runs against the synthetic fake provider (the `media-provider` image in
  [component-lock.json](../../component-lock.json)). It does no real media
  generation and checks run status, so no provider callback route is published.
- Time is not an installed service.
- Computers use the template's DeepInfra model provider.
- Hub's `computers.handbook` is the text of
  [computer/instructions.md](../../computer/instructions.md).
- `computer-v1`'s `release_note` in `installation.toml` is the note the running template
  carried, as `plan` read it on 2026-10-25 (UTC); `factory-v1` carries none.

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
and every image Bioma built, by the digest the cluster runs, as read on 2026-10-25
(UTC). Core's component-lock format holds one revision per Veoveo repository and no
other repository, so these provenances are here:

| Image | Built from |
|---|---|
| `openshell-gateway` | OpenShell `c80bda2013a5656bc2421a38013463709481671f`, whose `GetGatewayInfo` reports the supervisor and sandbox runtime images every new sandbox runs |
| `openshell-supervisor`, `openshell-sandbox` | OpenShell `49761d1eb3dc45f6f8f2b69b762d8316a7f217a7` and `1ab0e2386cbd943ec84a8701cd5d54dfa68e55a7`. Every sandbox created since 19:07 UTC on 2026-10-30 runs them: Hub, the services and the Computers restarted since; a factory instance takes them at its next push |
| `lore` | Lore `4ee9f3382ec5b3b214713ce21ee0d48263501d84`, which tells its `auth_service` catalog's endpoint of each repository it creates and deletes, with the template's Lore Dockerfile at `9f21d3e`, whose build and runtime stages the current template keeps unchanged, published as `veoveo/lore:4ee9f338`. The Lore server, Hub, the factory sandboxes and the Computer all run this digest |
| `computer` | The template at `9f21d3e` over the `factory` image, with OpenCode `c5fb62662c9c6fcb5064ef191956ca0da14e1af9`; the current template's Computer build inputs are the same |
| `factory` | The template at `9f21d3e`, the base of the `computer` image; no workload runs it directly |
| `media-provider` | Media `6a73e52932d166e368ba8673277cadf8be1742b9`, target `fake-provider`; the lock's Media revision is the server's, `6bd5843` |
| `postgres` | The template at `ecdb5b5dcc621161c7e5905a243c1271b42daeff` |
| `hub-sdk-cli` | The SDK at `05273d1`, target `cli` |

The lock's `veoveo-template-installation` revision, `9f21d3e`, is the one the
`computer`, `factory` and `lore` images were built from; the files here follow the
template at `51f2c7b`. Bioma runs these component revisions where the template locks
each component's main:

| Component | Template's lock | Bioma runs |
|---|---|---|
| `veoveo-hub` | `2739757` | `ce3cada` |
| `veoveo-hub-sdk` | `a41c9cc` | `05273d1` |
| `veoveo-mcp-console` | `e855cac` | `acc4ba2` |
| `veoveo-mcp-artifact` | `ae29dc3` | `91e62be` |
| `veoveo-mcp-media` | `871e11d` | `6bd5843` |
| `veoveo-mcp-embedding` | `df07d1f` | `46fa002` |
| `veoveo-runtime-embedding` | `9850c04` | `109304d` |
| `veoveo-mcp-time` | `6f17481` | not installed |

## Differences from the template

Besides placeholder values, these files differ from the template:

| File | Difference | Reason |
|---|---|---|
| `component-lock.json` | Names Bioma's deployed revisions and images, the template's own revision, and no Time | The lock is what Bioma runs. Time is not installed |
| `installation.toml` | Cilium's values add `openshell/bioma/kubernetes/cilium-node.values.yaml` | Bioma keeps its node override in this repository |
| `kubernetes/tunnel-routes.yaml` | Leaves out the Media callback route | Bioma's Media checks run status against the fake provider |
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
