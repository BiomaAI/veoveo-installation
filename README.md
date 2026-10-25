# Bioma's Veoveo installation

This is Bioma's Veoveo installation, running on Linux K3s at `https://veoveo.bioma.ai`.
It is the reference implementation of
[veoveo-template-installation](https://github.com/VeoveoAI/veoveo-template-installation):
the repository to read to see a real installation.

It is laid out as if the template had produced it for Bioma. The files are the
template's Linux K3s path, at template revision
`c8582f54e5025020b6983702bfc479a4fc80048b`, with Bioma's values in place of the
template's placeholders. [openshell/bioma/](openshell/bioma/README.md) lists Bioma's
selections and every other difference from the template, with its reason. The
template's Mac and Docker development fixtures stay in the template.

| Path | Contents |
|---|---|
| [kubernetes/](kubernetes/README.md) | The K3s foundation, the [native workload bootstrap](kubernetes/WORKLOADS.md), Helm values, manifests and native policies |
| [computer/](computer/README.md) | The Computer image, OpenCode configuration, handbook and provider profiles |
| [factory/](factory/Dockerfile) | The factory base image and the Lore image build |
| [identity/](identity/README.md) | Hub's Entra identity catalog and its preparation helper |
| [openshell/](openshell/bioma/README.md) | Provider profiles, storage policies and Bioma's selections |
| [postgres/](postgres/README.md) | The PostgreSQL extension image |
| [component-lock.json](component-lock.json) | The deployed revisions and image digests |
| [DESIGN.md](DESIGN.md) | The installation's design |

## What is deployed

[component-lock.json](component-lock.json) records each component's source revision
and image digest. They were read from the running cluster's Pods and Helm values,
the cluster's image build record and Hub's seeded configuration on 2026-10-24
(UTC). The build record names the Lore revision of the factory's Lore image only
by its image tag.

## Status

What works, how it was checked and what is still open are in the
[qualification checklist](https://github.com/VeoveoAI/veoveo-docs/blob/main/QUALIFICATION_CHECKLIST.md).
The architecture is in
[ARCHITECTURE.md](https://github.com/VeoveoAI/veoveo-docs/blob/main/ARCHITECTURE.md), and the installation design in the
[template's DESIGN.md](https://github.com/VeoveoAI/veoveo-template-installation/blob/main/DESIGN.md).

## Not in this repository

- Credentials and private state: tokens, keys, passwords, `.env` files, TLS
  material and the operator's rendered private inputs.
- Per-person data: principal grants, Work Context memberships, repository
  registrations and assignments. Hub's live control plane owns them.
- The operator's own build and deployment scripts.

## Keeping it current

Merge reviewed template updates, fill their placeholders with Bioma's values and
record any other difference in [openshell/bioma/](openshell/bioma/README.md). Send
fixes that apply to every installation to the template. After a deployment, update
`component-lock.json` from the running cluster.
