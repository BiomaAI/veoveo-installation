# veoveo-template-installation

A Veoveo installation is one repository that records what an organization runs: its
domain, identity providers, tenants, who holds which roles, and which components it
runs at which revisions. Create yours from this template with **Use this template**,
named `veoveo-<installation>` in your organization, for example `BiomaAI/veoveo-bioma`.

Components register themselves with the Gateway and declare their own permissions, so
an installation names no server's internals. It decides only who may do what.

The defaults run a local installation on one workstation: SurrealDB in Docker Compose,
and each component in its own OpenShell environment.

## Contents

| Path | Purpose |
|---|---|
| `compose.yaml` | SurrealDB 3.3.0, pinned by digest and published on the loopback interface only |

## Local Installation

Requirements: Docker with Compose v2, and OpenShell 0.1.3 with a local gateway started
with `OPENSHELL_TELEMETRY_ENABLED=false`. On macOS, Docker Desktop 4.94 or newer with
host networking enabled.

Keep `VEOVEO_SURREAL_PASSWORD` and, optionally, `VEOVEO_SURREAL_PORT` (8000 by default)
in an uncommitted `.env` file next to `compose.yaml`, then start the database:

```sh
docker compose up -d --wait
```

Sandboxes reach the database at `host.openshell.internal` on that port. Each component
repository builds its own environment image and documents how to create its sandbox.

Names follow the Veoveo
[naming and format conventions](https://github.com/VeoveoAI/veoveo-core/blob/main/docs/CONVENTIONS.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
