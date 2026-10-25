# Agent Instructions

- This repository is Bioma's real installation: the reference implementation of
  `VeoveoAI/veoveo-template-installation`, laid out as if the template had produced
  it for Bioma. Keep its files the template's Linux K3s path with Bioma's values in
  place of the placeholders. Record Bioma's selections and every other difference
  from the template, with its reason, in `openshell/bioma/README.md`. Send reusable
  fixes to the template. Planning, qualification status and evidence belong in
  `VeoveoAI/veoveo-docs`; link to them rather than copying them here. Components own
  their build and check logic.
- The design is the template's
  [DESIGN.md](https://github.com/VeoveoAI/veoveo-template-installation/blob/main/DESIGN.md),
  with [DESIGN.md](DESIGN.md) and `openshell/bioma/README.md` for Bioma's selections.
  Change them in the same change as the configuration they describe.
- Keep `component-lock.json` equal to what is deployed: each component's revision
  and image digest, read from the running cluster. Update it after each deployment.
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
  Preserve ordinary Lore operations and upstream security boundaries. The factory
  branch guard belongs in Lore's existing pre-push hook and trusted configuration;
  it is not a comprehensive branch authorization or transport-expiry system.
  Credential lifecycle qualification stays separate in native OpenShell controls.
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
