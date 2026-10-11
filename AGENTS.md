# Agent Instructions

- This repository describes which environments to launch. Build, check and repair
  logic belongs to each component's own repository and environment.
- Use upstream images such as SurrealDB unmodified and pinned by digest. Verify the
  latest stable release at its source when changing a pin.
- Never commit credentials. Compose reads them from an uncommitted `.env` file.
- Name sandboxes and other runtime identifiers with the `vv-` short form described in
  the README.
- Validate with `docker compose config` and start the services on macOS and on Linux
  before pushing.
- Commit small, coherent changes. Commits carry no AI or tool attribution.
