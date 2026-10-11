# veoveo-deploy

This repository describes which environments to launch for a Veoveo installation and
nothing more. Components build, check and verify themselves inside their own
environments. Upstream infrastructure that runs outside OpenShell is described here as
Compose services.

## First slice

| Environment | Runs as | Sandbox name | Image | Policy |
|---|---|---|---|---|
| SurrealDB 3.3.0 | Compose service `surrealdb`, outside OpenShell | — | `surrealdb/surrealdb:v3.3.0`, pinned by digest | — |
| Core | OpenShell sandbox | `vv-core` | `veoveo-core:dev`, built from [veoveo-core](https://github.com/VeoveoAI/veoveo-core) | `openshell/policy.yaml` in that repository |
| Time | OpenShell sandbox | `vv-mcp-time` | `veoveo-mcp-time:dev`, built from [veoveo-mcp-time](https://github.com/VeoveoAI/veoveo-mcp-time) | `openshell/policy.yaml` in that repository |
| Gateway | OpenShell sandbox | `vv-srv-gateway` | `veoveo-service-gateway:dev`, built from [veoveo-service-gateway](https://github.com/VeoveoAI/veoveo-service-gateway) | `openshell/policy.yaml` in that repository |

The Gateway's exposure, the bootstrap identities and the namespace bindings are not
decided yet. MCP servers dial out to the Gateway, so the Time environment needs no
inbound path.

## Sandbox names

OpenShell limits sandbox names to 19 characters. Sandboxes and other runtime
identifiers use `vv-` plus a short kind and the component name: `srv` for services,
`mcp` for MCP servers, `rt` for runtimes, `app`, `sdk`, `tpl` for templates, `demo`
for showcases and `qual` for qualification suites. Repositories without a kind use
`vv-<name>`.

## SurrealDB

`compose.yaml` runs SurrealDB with RocksDB storage on a named volume. It refuses to
start until `SURREAL_PASS` holds the root password, and `SURREAL_PORT` selects the host
port, 8000 by default. Keep both in an uncommitted `.env` file next to `compose.yaml`.

```sh
docker compose up -d --wait
```

Sandboxes reach the database at `host.openshell.internal` on that port, and each
environment's policy names that endpoint.

## Environments

Each component repository builds its own `dev` image. Clone the repository, build the
image and create its sandbox, for example for Time:

```sh
docker build --target dev -t veoveo-mcp-time:dev .
openshell sandbox create --name vv-mcp-time --from veoveo-mcp-time:dev \
  --policy openshell/policy.yaml --env HOME=/sandbox --detach -- sleep infinity
```

## Requirements

Docker with Compose v2, and OpenShell 0.1.3 with a local gateway started with
`OPENSHELL_TELEMETRY_ENABLED=false`. On macOS, Docker Desktop 4.94 or newer with host
networking enabled.

## License

Apache-2.0. See [LICENSE](LICENSE).
