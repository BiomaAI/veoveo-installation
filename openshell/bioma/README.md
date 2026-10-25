# Bioma's selections

This repository follows [veoveo-template-installation](https://github.com/VeoveoAI/veoveo-template-installation)
at `51f2c7bd51e9d708a91b56e6f36ca56073302fa4`, the template's `cleanup` branch over its
main `67b7032e988a71d80938c4e4e79897f78c3a8152`. The shared files carry Bioma's
values in place of the template's placeholders, and [DESIGN.md](../../DESIGN.md) is the
template's, verbatim. Its installer (`installer/`), its declaration (`installation.toml`)
and [DESIGN.md](../../DESIGN.md) follow the template's `installer` branch at
`ec628b3445ce946500c27a62f7c6f238a18d7b96`. This page lists what Bioma selected and
every other place where a file differs from the template.

## Placement

- One Linux amd64 node (Ubuntu 24.04.5) running K3s `v1.36.5+k3s1`.
- [cilium-node.values.yaml](kubernetes/cilium-node.values.yaml) is the template's
  private Cilium node override (`$PRIVATE/cilium-node.yaml` in the
  [foundation steps](../../kubernetes/README.md)). It holds the node's API address.
- The OpenShell gateway ID is `openshell`. The workspaces are `vv-control` (Hub),
  `vv-services` (MCP servers), `vv-factory` (factory sandboxes) and `installation`
  (the Computer and factory templates). Their managed namespaces are
  `openshell-openshell-<workspace>`, the names the builder's and log store's network
  policies use.
- The embedding runtime uses the node's GPU through the NVIDIA device plugin.

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

## Not yet deployed

Two files here are ahead of what the cluster runs, as read on 2026-10-25 (UTC):

- Hub's active `computers.handbook` is still the text of `computer/instructions.md` at
  the template's `1b56e68`, without the paragraph on the Hub CLI. The current text
  takes effect when it is published through the live control plane.
- The running Lore server's `lore-settings` still holds the `factory_branch` hook
  with no assignments, which admits every push. [lore.toml](../../kubernetes/lore.toml)
  has no hook; it takes effect when `lore-settings` is recreated from it and Lore
  restarts.

## Deployed revisions

[component-lock.json](../../component-lock.json) names each Veoveo component's revision
and every image Bioma built, by the digest the cluster runs, as read on 2026-10-25
(UTC). Core's component-lock format holds one revision per Veoveo repository and no
other repository, so these provenances are here:

| Image | Built from |
|---|---|
| `openshell-gateway`, `openshell-supervisor`, `openshell-sandbox` | OpenShell `491b3503d39f3ba83a25a309f52e52e20e304b03`, the template's pin. Hub, console, the factory sandboxes and the Computer run this supervisor and sandbox runtime; Artifact, Media, the Media provider, Embedding and its runtime still run those of OpenShell `d1d4da39941ecf809d9b0dee51032277cbc42ea4` (`supervisor@sha256:6ce6d7b2…`, `sandbox@sha256:d2a791ff…`) until they next start |
| `lore` | Lore `4b7b7e236419414b4a0c67ecd66ca2409f19d35c` with the template's Lore Dockerfile at `9f21d3e`, whose build and runtime stages the current template keeps unchanged, published as `veoveo/lore:drill-20261025`. The Lore server, Hub, the factory sandboxes and the Computer all run this digest |
| `computer` | The template at `9f21d3e` over the `factory` image, with OpenCode `c5fb62662c9c6fcb5064ef191956ca0da14e1af9`; the current template's Computer build inputs are the same |
| `factory` | The template at `9f21d3e`, the base of the `computer` image; no workload runs it directly |
| `media-provider` | Media `6a73e52932d166e368ba8673277cadf8be1742b9`, target `fake-provider`; the lock's Media revision is the server's, `6bd5843` |
| `postgres` | The template at `ecdb5b5dcc621161c7e5905a243c1271b42daeff` |
| `hub-sdk-cli` | The SDK at `a41c9cc`, target `cli` |

The lock's `veoveo-template-installation` revision, `9f21d3e`, is the one the
`computer`, `factory` and `lore` images were built from; the files here follow the
template at `51f2c7b`. Bioma runs these component revisions where the template locks
each component's main:

| Component | Template's lock | Bioma runs |
|---|---|---|
| `veoveo-hub` | `d718d02` | `e895369`; `d718d02` adds only documentation |
| `veoveo-hub-sdk` | `a41c9cc` | `a41c9cc` |
| `veoveo-mcp-console` | `e855cac` | `a8f5d29` |
| `veoveo-mcp-artifact` | `ae29dc3` | `a0566b8` |
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
| `kubernetes/openshell.values.yaml` | The three OpenShell image digests are filled in | They are the images Bioma deployed |
| `kubernetes/postgres.yaml`, `hub-config-pvc.yaml`, `media-provider-config-pvc.yaml`, `postgres-client-ca.yaml`, `seed-service-configs.yaml` | The image markers name the deployed PostgreSQL image and the pinned `debian:trixie-slim` copy utility | These values are rendered here |
| Comments and sentences that say to render the host, image or gateway ID (`kubernetes/README.md`, `WORKLOADS.md`, `lore.toml`, `embedding-storage.yaml`, `postgres.yaml`, `seed-service-configs.yaml`, `tunnel-routes.yaml`, `policies/console.yaml`, `policies/factory-base.yaml`, `openshell/providers/factory-lore.yaml`, `factory-registration.yaml`, `lore.yaml`) | Reworded | These values are already rendered here |
| `README.md`, `AGENTS.md` | Describe this repository | Bioma's repository, not the template |
| Links to template files left out of this repository | Point to the template at `51f2c7b` | These files are the template's Mac and Docker fixtures and its Docker-era reference documents |

`lore.yaml` and the Hub, Computer and factory driver configurations keep the
template's `@image:lore@` and `@image:hub-sdk-cli@` placeholders, which the operator
fills from the lock into private copies, as the template's
[naming each image once](../../kubernetes/README.md#naming-each-image-once) says.

The template files left out are its Mac and Docker development fixtures: Compose,
local Keycloak and Envoy, the Docker gateway configuration, policies and mounts, the
Docker Lore configuration, the Docker variants of the Computer files, and the
Docker-era `openshell/` documents. Time's registration profile,
`openshell/providers/time-registration.yaml`, is left out too, because Time is not
installed.
