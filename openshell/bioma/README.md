# Bioma's selections

This repository follows [veoveo-template-installation](https://github.com/VeoveoAI/veoveo-template-installation)
at `c8582f54e5025020b6983702bfc479a4fc80048b`. The shared files carry Bioma's
values in place of the template's placeholders. This page lists what Bioma selected
and every other place where a file differs from the template.

## Placement

- One Linux amd64 node (Ubuntu 24.04.5) running K3s `v1.36.5+k3s1`.
- [cilium-node.values.yaml](kubernetes/cilium-node.values.yaml) is the template's
  private Cilium node override (`$PRIVATE/cilium-node.yaml` in the
  [foundation steps](../../kubernetes/README.md)). It holds the node's API address.
- The OpenShell gateway ID is `openshell`. The workspaces are `vv-control` (Hub),
  `vv-services` (MCP servers), `vv-factory` (factory sandboxes) and `installation`
  (the Computer template). Their managed namespaces are `openshell-openshell-<workspace>`.
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
| Hub's Entra broker application (confidential Web app, `/oauth/callback`) | `853550a7-5fd4-421c-abd2-bea0216fa579` |
| OpenShell gateway resource application (gateway OIDC audience) | `8a6d434f-8c4c-4e2c-9756-9b2d94118d17` |
| Gateway app roles, in the `roles` claim | `openshell-admin`, `openshell-user` |
| Hub access-token signing key ID | `nr-CyVKgU-7yqss1O9KW-8gr4WMw8a1JWOupDeCieFc` |
| Hub installation names | tenant `reference`, Work Context `reference-work`, policy revision `reference-policy` |
| Hub's Entra identity provider and broker client record | `entra`, with secret reference `entra_client_secret` |

Principal object IDs, grants, Work Context memberships, repository registrations and
assignments are per-person data. They are not in this repository.
[entra.example.json](../../identity/entra.example.json) keeps the template's
example principals.

## Services

- Hub, plus Artifact, Media, Embedding and console in `vv-services`.
- Media runs against the synthetic fake provider (`veoveo-mcp-media-provider` in
  [component-lock.json](../../component-lock.json)). It does no real media
  generation, so no provider callback route is published.
- Time is not an installed service.
- Computers use the template's DeepInfra model provider.
- Hub's `computers.handbook` is the text of
  [computer/instructions.md](../../computer/instructions.md).

## Differences from the template

Besides placeholder values, these files differ from the template:

| File | Difference | Reason |
|---|---|---|
| `identity/entra.example.json` | Adds the `computer` profile for `/mcp/computer` | Bioma runs it. The K3s Hub fragment assumes it, and the template catalog does not define it. |
| `identity/entra.example.json` | Adds the `installation-administration` rule to `reference-policy` | Bioma runs it. [WORKLOADS.md](../../kubernetes/WORKLOADS.md) requires it for the admin control-plane route. |
| `identity/entra.example.json` | Leaves out `nativeUpstreams` | The template's block describes the Mac gateway and a Time binding. On K3s, `kubernetes/hub.example.json` defines `nativeUpstreams`. |
| `kubernetes/hub.example.json` | Adds the Embedding binding | Bioma runs Embedding. |
| `kubernetes/hub.example.json` | The broker client record is `entra`, with all three resources | It is the same record `identity/entra.example.json` defines, so the merged record is the one Bioma runs. |
| `kubernetes/tunnel.yaml` | The Secret volume projects only the `token` key | Matches the running Deployment. |
| Comments that say to render the host, image or gateway ID | Reworded | These values are already rendered here. |
| `README.md`, `AGENTS.md`, `DESIGN.md` | Describe this repository | Bioma's repository, not the template |
| Links to template files left out of this repository | Point to the template at `c8582f5` | These files are the template's Mac and Docker fixtures and its Docker-era reference documents. |

The template files left out are its Mac and Docker development fixtures: Compose,
local Keycloak and Envoy, the Docker gateway configuration, policies and mounts, the
Docker Lore configuration, the Docker variants of the Computer files, and the
Docker-era `openshell/` documents.
