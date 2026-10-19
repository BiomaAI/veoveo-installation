# Bioma Veoveo installation

Bioma's reference deployment at **https://veoveo.bioma.ai**, derived from the
[Veoveo installation template](https://github.com/VeoveoAI/veoveo-template-installation).
This repository records a real Linux installation's native configuration and
qualification status. VeoveoAI owns reusable platform and installation mechanisms;
this repository owns Bioma's deployment choices.

## Deployment

OpenShell's native gateway and the dedicated Cloudflare tunnel run as host services
on Linux x86_64. Hub, Time, Artifact and Media use native OpenShell Docker sandboxes.
PostgreSQL and SeaweedFS use the template's trusted bootstrap. Microsoft Entra
authenticates the operator and Hub users. Hub issues application grants and retains
full MCP Tasks support.

| Entry point | Purpose |
| --- | --- |
| `https://veoveo.bioma.ai` | Hub OAuth and MCP; only Media's signed callback path routes directly to Media |
| `https://veoveo-objects.bioma.ai` | Native SeaweedFS S3 HTTPS, preserving signed request authority and bytes |
| Native OpenShell management | Private host endpoint for authenticated management and approved forwarding |

Follow the [native reference procedure](openshell/REFERENCE.md) with
[Bioma's native configuration](openshell/bioma/). Other template components remain
available for reference; their presence does not mean they are enabled. This Linux
selection does not run the local Keycloak profile or identity edge. Existing Mac
and Lore/factory qualification remains separate.

[Cloudflare's native ingress configuration](openshell/bioma/cloudflared.json)
records the selected routes, verified origin names and this host's native public
CA path. The tunnel token stays private. Apply its `ingress` array through the
existing remotely managed tunnel configuration; the file does not create DNS,
credentials or a connector. Other hosts must select their own verified CA path.

| Component | Selected source revision |
| --- | --- |
| OpenShell | `6589a918a7a84640969f9f77b852695e210d713f` |
| Hub | `ec9f7f59be0e74135e5ed8179e65e360c701cf6c` |
| Time | `9874293db5ffdc6be260dd60094e7b1f97fe5e3c` |
| Artifact | `ce0a766e3556ce02f899b9dc37466f5d1be013c0` |
| Media | `774be1eddfe387a95a461a88c7a0b2b2d48d84c7` |

Build through each component's existing procedure and select its resulting immutable
image in native OpenShell. These pins do not claim registry publication. Exact local
image identities and runtime receipts belong in the
[execution checklist](https://github.com/VeoveoAI/veoveo-docs/blob/main/OPENSHELL_HARDCUT_PLAN.md#reference-linux-deployment-and-signed-wavespeed-webhook-goal).

## Qualification status

As of 2026-10-18, native Linux builds and component checks pass. Native OpenShell
operator login through Entra is verified, and the reference tunnel is connected.
Fresh PostgreSQL is healthy. SeaweedFS verifies TLS and denies anonymous S3 requests
through both its origin and public hostname. Hub, Time, Artifact, Media and the
synthetic provider fixture are Ready in native OpenShell sandboxes. Hub passes
canonical public discovery/JWKS checks; service registration and database migrations
pass. Artifact's bucket-scoped storage identity passes object and multipart
operations and is denied access to an unrelated bucket. The fixture holds fake
credentials only; it has no real WaveSpeed credentials.
Media's native/public callback ingress passes Host admission after selecting the
SDK's existing loopback-host allowance. Unsigned callback probes are rejected;
this does not yet qualify a real provider event. The same sandbox, persistent
volumes and signing key survive the configuration restart.
The restricted Hub forwarder completed a scheduled credential renewal at
21:06:55 UTC, observed without manual rotation.

Administrator and ordinary-member Entra-to-Hub PKCE logins and independent
application-token signature/identity checks pass. Both distinct grants are in native
credential custody. The SDK client discovers 40 tools through the public Hub;
fresh typed Time calls pass for both identities after the source-derived original
access-token expiry bounds, with unchanged native references and sandbox process.
All seven deployed Time cases pass, including permission refusal, Task completion,
cancellation, subscriptions and reconnect. Five private Artifact cases pass.
The corrected large-transfer fixture completed multipart upload and server
verification of 1,076,887,552 bytes, but Hub converted the ended upstream listener
into an internal error before the test observed completion. Hub's correction now
preserves normal listener completion so the existing SDK can re-subscribe and
reconcile state. Its HTTP-disconnect regression and both platform component gates
pass, and the corrected revision is deployed with public discovery and a routed
Time call verified. The subsequent large case exposed the SDK's separate limit of
three total listener openings: the client stopped following before the backend
completed verification successfully. SDK recovery correction `4839146` now passes
both platform component gates and is adopted by the updated Artifact and Media
clients. Time's and Media's standard missing-Tasks-capability corrections also pass
both platform gates. The selected service revisions above are deployed and Ready;
the full large-object digest/range/deletion case and updated deployed suites remain
pending.
Full Artifact qualification, fake-provider Media and restart persistence remain open.
The real signed WaveSpeed callback and final OpenCode/MiMo run are also pending;
this Linux deployment has
made no paid generation or model-driven acceptance call. GPU/CUDA and general
environment composition remain separate work.

The operator selected empty application state and removal of the retired Linux
stack. That development reset is not a production migration procedure. New state
and identities must persist across subsequent restarts.

## Credentials and template updates

Native policies, public endpoints and reviewed source selections belong in Git.
Keep `.env`, `state/`, `tls/`, private keys, provider secrets, grants and signed URLs
out of Git. Use the existing private configuration and native OpenShell credential
custody. Cloning this repository does not confer operator or application access.

The repository shares Git history with the template. Its current reviewed base is
`7e113b2d871d1a0c0e5dd056b134acdbf0c899f2`. Configure the upstream after cloning:

```sh
git remote add upstream https://github.com/VeoveoAI/veoveo-template-installation.git
git fetch upstream
```

Review and merge selected upstream changes, retain Bioma's native configuration,
and run the applicable checks and deployed qualification before updating a running
installation. Send reusable fixes to the template first. Keep this README and the
execution checklist aligned with actual deployed revisions and evidence.

See the [platform architecture](https://github.com/VeoveoAI/veoveo-docs/blob/main/LORE_OPENSHELL_INTEGRATION.md)
and [visual guide](https://github.com/VeoveoAI/veoveo-docs/blob/main/diagrams/veoveo-platform.html)
for responsibilities and integration scope.
