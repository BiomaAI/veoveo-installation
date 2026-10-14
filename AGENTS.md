# Agent Instructions

- This repository is a template for Veoveo installations. It holds only installation
  decisions: domain, identity providers, tenants, roles and grants, and which components
  run at which revisions. It never names a server's internals; components register and
  declare themselves.
- Its defaults run a local installation on one workstation. Keep them working, because
  every installation starts from them.
- Build, check and repair logic belongs to each component's own repository and
  environment. Planning documents belong in `veoveo-docs`.
- Use upstream images such as PostgreSQL, SeaweedFS and Envoy unmodified and pinned by
  digest, and Lore from `VeoveoAI/lore` pinned to one commit. Verify the latest stable
  release at its source when changing a pin.
- Never commit credentials. Compose reads them from an uncommitted `.env` file. The
  Envoy edge adds the secrets environments use to their requests, so an environment
  holds only a placeholder, and the Lore token service keeps each environment's Lore
  token readable only by the setgid Lore client. A component that signs or verifies
  with a secret itself, such as Artifact with the object store's credential or Media
  with the provider's webhook secret, receives only that secret as an owner-only file
  piped in without printing it.
- Committed files name the installation's public origin only by the placeholder
  `https://veoveo.example.com`. The real origin and the tunnel's connector token live in
  the uncommitted `.env`.
- Names, identifiers and formats follow the
  [naming and format conventions](https://github.com/VeoveoAI/veoveo-core/blob/main/docs/CONVENTIONS.md);
  Compose services and containers use the `vv-` short form, and their network names end
  in `.internal`.
- Validate with `docker compose config` and start the services on macOS and on Linux
  before pushing.
- Commit small, coherent changes. Commits carry no AI or tool attribution.
