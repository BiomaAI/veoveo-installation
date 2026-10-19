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
| Hub | `ed6778f6a7e61df4f4c42241a589d9450f2bd63f` |
| Time | `e607b2e734a307965951022945b3a1383fb51e94` |
| Artifact | `00c8e93f5ca3ffe9137773754a4945c6d349b3bf` |
| Media | `4e8504b2c9bc72b0b249a8cf122e29983634d2e8` |

Build through each component's existing procedure and select its resulting immutable
image in native OpenShell. These pins do not claim registry publication. Exact local
image identities and runtime receipts belong in the
[execution checklist](https://github.com/VeoveoAI/veoveo-docs/blob/main/OPENSHELL_HARDCUT_PLAN.md#reference-linux-deployment-and-signed-wavespeed-webhook-goal).

## Qualification status

Remote access is restored. All seven selected source repositories are published
and pass their component gates both on Mac (Linux ARM64 containers) and on the
actual Linux x86_64 host: Core `433ed5f`, SDK `b0b8d86`, Hub `ed6778f`, Time
`e607b2e`, Artifact `00c8e93`, Media `4e8504b` and MCP template `b39a604`.
Matching runtime builds pass, and all four fresh native application sandboxes plus
the synthetic provider fixture are Ready at the revisions selected above.
OpenShell remains at `6589a918`.

The authorized disposable PostgreSQL/SeaweedFS application-state reset is complete,
without backups or history migration. Source and trusted installation/identity
configuration remain rebuild inputs. This development reset is not a production
migration procedure; normal durable ownership still applies across routine
sandbox restarts.

Native OpenShell Entra operator authentication and the reference tunnel are
verified. Fresh administrator and ordinary-member Entra-to-Hub PKCE grants pass
independent signature and identity checks and are restored to native credential
custody. These are distinct human principals; the positive caller has both
administrator and billed authority. The fixture holds fake credentials only,
with no real WaveSpeed credentials.

Public S3 TLS is verified. Artifact's dedicated storage key is denied both List
and Get access to an existing unrelated bucket/object. `ListBuckets` returns the
filtered visible bucket set, and the administrative `ListUsers` request returns
HTTP 403. These isolation checks alone do not prove multipart behavior; the
separate fresh six-case baseline below includes the full large multipart proof.
Media's signed-callback ingress previously passed Host admission and refused
missing/wrong signatures. One real signed Events completion now passes, as below.

Time's fresh seven-case baseline passes in 14.61 seconds libtest (14.662 seconds
outer Exec). Artifact's fresh six-case private baseline passes in 406.48 seconds
libtest (406.534 seconds outer Exec), including the large unknown-size multipart
case. Media's six-case fake baseline also passes in 51.28 seconds libtest
(51.336316 seconds outer Exec). All three terminal restart verifies pass on the
same prepared records; initial Artifact/Media Ready-only failures are retained,
and routed application reads preceded successful verifies. Media's in-flight
Media+Hub restart passes in 62.00 seconds with the same Task/prediction, one
independently observed fake submission and pushed completion. Both roles' fresh
calls succeed beyond the conservative source-derived original-JWT expiry bound
in one SDK runner with unchanged opaque handles; this is not uninterrupted-stream
or decoded-token-expiry evidence. Time's reviewed in-flight restart now passes in
24.91 seconds with the same Task Working after restart, a reopened subscription,
pushed completion and the expected 64-window result. Earlier slow-boundary and
invalid-harness attempts remain historical, not product failure claims. Final
bounded MiMo qualification remains incomplete after the two timed-out attempts
recorded below; both used the real Artifact retrieval scenario. Earlier frozen-source
qualification includes the complete 1,076,887,552-byte upload in 65 parts,
server checksum verification, a 200-byte boundary range, deletion and stored-byte
release (419.65 seconds). That historical pass does not qualify the newly deployed
typed-contract stack. See the
[execution checklist](https://github.com/VeoveoAI/veoveo-docs/blob/main/OPENSHELL_HARDCUT_PLAN.md#reference-linux-deployment-and-signed-wavespeed-webhook-goal)
for its exact source/runtime receipts and current gates.

One real Linux WaveSpeed signed Events generation now passes independently of
the remaining regression/restart gates. `wavespeed-ai/flux-schnell` used one image,
seed 42 and 1024 × 1024 PNG output, with the orange-robot/green-seedling prompt
recorded in the [dated receipt](https://github.com/VeoveoAI/veoveo-docs/blob/main/OPENSHELL_HARDCUT_PLAN.md#linux-real-wavespeed-signed-events-receipt--2026-10-19).
The 26.034106-second acceptance interval includes callback, storage and billing;
it is not pure inference time. The accepted/applied final callback settled the
generation with zero status checks; one separate billing check confirms per-Task
estimate and actual USD 0.003. Independent full download and decode match the
private Artifact: PNG 1024 × 1024, 883,996 bytes, SHA-256
`007af757d14221e544098adc5a1e37488f7e57818c85c9e3d91e97587d646b96`.
An initial catalog refusal created no Task or dispatch; correcting the existing
native provider credential resolved its underlying HTTP 401. Independent retrieval
needed one exact SDK-runner tool-policy addition. Bounded native logs show one
admitted generation POST, not a lossless provider request ledger.

Two bounded OpenCode/MiMo attempts used explicit Build and
`deepinfra/XiaomiMiMo/MiMo-V2.6-Pro`, eight steps and a 240-second model deadline,
with their own OAuth grant and no Media generation. Both timed out without
completed tool results/accounting or a saved file; provider activity and billing
are not measured by those incomplete receipts. The first killed process left a
recoverable claim; native standalone deletion retired that disposable session
after retaining evidence. The corrected second attempt (06:57:25.554651 UTC)
used supported native interruption: 39.06 ms cleanup, claim released, zero resume
attempts; model phase 240.003101 seconds, total 242.127631 seconds. The local
synthetic cancellation check passed without inference. The revised live-observer
fixture also passes: one synthetic request/frame, nonempty reasoning delta counted
in a private metadata-only log with no raw text retained, interruption and claim
release (8.599 ms cleanup). The current observed 600-second attempt retains the
same eight steps and generation denial; its outcome and final client qualification
remain pending.
The free restored Media catalog/member-refusal case also passes (0.38 seconds),
without a generation or an exact selected-model assertion. See the exact
[attempt receipts](https://github.com/VeoveoAI/veoveo-docs/blob/main/OPENSHELL_HARDCUT_PLAN.md#reference-linux-deployment-and-signed-wavespeed-webhook-goal).
The independently decoded real Artifact and signed callback remain qualified;
no second paid generation is needed. GPU/CUDA and general environment composition
remain separate work.

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
