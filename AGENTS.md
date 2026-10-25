# Agent Instructions

- This repository is Bioma's real installation: the reference implementation of
  `VeoveoAI/veoveo-template-installation`, laid out as if the template had produced
  it for Bioma. Keep its files the template's Linux K3s path with Bioma's values in
  place of the placeholders. Record Bioma's selections and every other difference
  from the template, with its reason, in `openshell/bioma/README.md`. Send reusable
  fixes to the template. Planning, qualification status and evidence belong in
  `VeoveoAI/veoveo-docs`; link to them rather than copying them here. Components own
  their build and check logic.
- The repository holds the template's installer (`installer/`, Rust), unchanged, and
  Bioma's declaration of what it applies, `installation.toml`. Bring the installer
  over from the template; record any change Bioma needs in it as a difference.
  Its check is `docker build -f installer/Dockerfile --target check .`.
- The substrate, what `installation.toml` declares, changes only through
  `veoveo-installer plan` and `apply` ([installer/README.md](installer/README.md)),
  never by hand with `kubectl`, `helm` or `openshell`. Run `plan` first. Only the
  manual steps the [Kubernetes guide](kubernetes/README.md) keeps are done by hand.
- The design is the template's: [DESIGN.md](DESIGN.md) is its copy, verbatim, at the
  template revision this repository follows. Bioma's selections are in
  `openshell/bioma/README.md`. Change it in the same change as the configuration it
  describes, and change the design in the template.
- Keep `component-lock.json` equal to what is deployed, in core's component-lock
  format: each component's revision and each image's digest, read from the running
  cluster. Update it after each deployment.
- Linux deployment uses K3s foundation controllers and OpenShell's native Kubernetes
  driver for Hub/MCP, Computer and factory workloads. Mac development and test
  fixtures stay in the template, not here. Use native APIs, lifecycle, credential
  store, policy and diagnostics. Do not add an orchestrator, Helm sandbox inventory,
  token worker or second launcher.
- Real provider tokens, signing keys, operator state, bootstrap volumes and Docker
  access stay outside author and agent-controlled service workloads. Use native
  OpenShell credential mediation. Unsupported enforcement fails closed.
- Prefer upstream configuration and extension points. Maintained, revision-pinned
  VeoveoAI security/transport patches are allowed by the accepted architecture.
  Preserve ordinary Lore operations and upstream security boundaries. Lore runs no
  hook. A factory instance's Lore access is read-only through its `vv-factory-lore`
  provider profile, which admits only the read methods of `lore clone` and
  `lore sync --reset`; Lore's own permissions decide the rest. Credential lifecycle
  qualification stays separate in native OpenShell controls.
- Entra authenticates humans. Hub's existing issuer and live revisioned control
  plane own explicit repository assignments/native Lore tokens; native Lore enforces
  its unchanged token/permission contract. OpenShell renews/injects factory grants;
  human Lore refresh remains private to each Computer. Creating a repository through
  Hub makes its creator the owner; no other repository grant is automatic, and no
  administrator role grants repositories. Do not restore the withdrawn direct-IdP
  grant helper, Desktop adapter, signer or ingress, or add a token worker, custom
  Lore rules or global grants.
- The platform never writes into a Computer's `/sandbox`; it is the person's home.
- Never commit credentials, private state or per-person data: principal grants,
  memberships, repository registrations and assignments. `.env`, TLS/private state
  and local backups remain ignored and excluded from build contexts. Commit only
  `.example` forms of identity catalogs. Do not commit the operator's build or
  deployment scripts.
- During rapid development, application data is disposable for authorized resets
  on breaking contracts; do not add migrations, backward compatibility or backups
  merely to retain development data. Retain source and trusted installation/identity
  configuration as rebuild inputs. Preserve normal durable ownership across routine
  sandbox lifecycle; revisit retention when production data enters scope.
- Use upstream bootstrap images pinned by digest. Verify releases when changing pins.
  Bioma's files use its actual public domain and public application IDs.
- Commit coherent changes without AI attribution.
