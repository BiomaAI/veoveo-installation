# Bioma's Veoveo installation

This is Bioma's Veoveo installation, running on Linux K3s at `https://veoveo.bioma.ai`.
It is the reference implementation of
[veoveo-template-installation](https://github.com/VeoveoAI/veoveo-template-installation):
the repository to read to see a real installation.

It is laid out as if the template had produced it for Bioma. The files are the
template's Linux K3s path, at template revision
`51f2c7bd51e9d708a91b56e6f36ca56073302fa4`, with Bioma's values in place of the
template's placeholders. [openshell/bioma/](openshell/bioma/README.md) lists Bioma's
selections and every other difference from the template, with its reason. The
template's Mac and Docker development fixtures stay in the template.

| Path | Contents |
|---|---|
| [installer/](installer/README.md) | The template's `veoveo-installer`, which applies [installation.toml](installation.toml) |
| [kubernetes/](kubernetes/README.md) | The K3s foundation, the [native workload bootstrap](kubernetes/WORKLOADS.md), Helm values, manifests and native policies |
| [computer/](computer/README.md) | The Computer image, OpenCode configuration, handbook and provider profiles |
| [factory/](factory/Dockerfile) | The factory base image and the Lore image build |
| [identity/](identity/README.md) | Hub's Entra identity catalog and its preparation helper |
| [openshell/](openshell/bioma/README.md) | Provider profiles, storage policies and Bioma's selections |
| [postgres/](postgres/README.md) | The PostgreSQL extension image |
| [component-lock.json](component-lock.json) | The deployed revisions and image digests |
| [DESIGN.md](DESIGN.md) | The installation's design, the template's copied verbatim |

## What is deployed

[component-lock.json](component-lock.json) records each component's source revision
and each image's digest, in core's component-lock format. The digests were read from
the running cluster's Pods, their image volumes and the gateway's Helm values on
2026-10-25 (UTC); the revisions come from the cluster's image build record. The
revisions the format cannot hold, of OpenShell, Lore and OpenCode, are in
[openshell/bioma/](openshell/bioma/README.md#deployed-revisions).

## Status

What works, how it was checked and what is still open are in the
[qualification checklist](https://github.com/VeoveoAI/veoveo-docs/blob/main/QUALIFICATION_CHECKLIST.md).
The architecture is in
[ARCHITECTURE.md](https://github.com/VeoveoAI/veoveo-docs/blob/main/ARCHITECTURE.md), and the installation design in the
[template's DESIGN.md](https://github.com/VeoveoAI/veoveo-template-installation/blob/main/DESIGN.md).

## Not in this repository

- Credentials and private state: tokens, keys, passwords, `.env` files, TLS
  material and the operator's private directory.
- Per-person data: principal grants, Work Context memberships, repository
  registrations and assignments. Hub's live control plane owns them.
- The operator's own build and deployment scripts.

## Keeping it current

Merge reviewed template updates, fill their placeholders with Bioma's values and
record any other difference in [openshell/bioma/](openshell/bioma/README.md). Send
fixes that apply to every installation to the template. After a deployment, update
`component-lock.json` from the running cluster.
