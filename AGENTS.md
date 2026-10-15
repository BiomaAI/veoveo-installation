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
  digest, and unmodified Lore from `EpicGames/lore` pinned to its release commit. Verify the latest stable
  release at its source when changing a pin.
- Never commit credentials. `.env` and private TLS/state files stay ignored and out of
  build contexts. Coding agents run only in `vv-dev-*`, never in the trusted `runtime`
  containers. Dev volumes contain source, caches and disposable test state only.
- Envoy authenticates development Lore and inference requests. Tokens, signing keys,
  runtime volumes and the Docker socket never enter a dev container. Select each Lore
  credential by the listener's private network and actual TCP peer, never by an
  agent-controlled header. Keep `no-new-privileges` and all capabilities dropped in dev.
- Runtime containers contain no Lore client or token mounts. Use the isolated reviewer
  for repository administration and keep `no-new-privileges` enabled everywhere.
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
