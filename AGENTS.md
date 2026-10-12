# Agent Instructions

- This repository is a template for Veoveo installations. It holds only installation
  decisions: domain, identity providers, tenants, roles and grants, and which components
  run at which revisions. It never names a server's internals; components register and
  declare themselves.
- Its defaults run a local installation on one workstation. Keep them working, because
  every installation starts from them.
- Build, check and repair logic belongs to each component's own repository and
  environment. Planning documents belong in `veoveo-docs`.
- Use upstream images such as PostgreSQL unmodified and pinned by digest. Verify the
  latest stable release at its source when changing a pin.
- Never commit credentials. Compose reads them from an uncommitted `.env` file, and
  environments receive secrets through OpenShell providers.
- Names, identifiers and formats follow the
  [naming and format conventions](https://github.com/VeoveoAI/veoveo-core/blob/main/docs/CONVENTIONS.md);
  sandboxes, providers and Compose services use the `vv-` short form.
- Validate with `docker compose config` and start the services on macOS and on Linux
  before pushing.
- Commit small, coherent changes. Commits carry no AI or tool attribution.
