# Bioma Kubernetes installation

Current Linux architecture: K3s manages CloudNativePG PostgreSQL, official-chart
SeaweedFS, native Lore, the OpenShell gateway and the existing tunnel. OpenShell's
native Kubernetes driver owns dynamic Hub/MCP, Computer and factory sandboxes.
Entra authenticates humans; Hub owns native Lore grants; Lore behavior is unchanged.

Use [current Bioma Kubernetes selections](openshell/bioma/kubernetes/README.md),
[generic foundation inputs](kubernetes/README.md) and
[native workload bootstrap](kubernetes/WORKLOADS.md). No platform Compose launch
path remains in this Linux branch. Mac source/component/integration development
and optional local identity fixtures remain in the generic template; no Mac cluster.

Kubernetes application deployment/acceptance is **pending**. Source integration,
controller readiness or old Docker receipts do not establish Kubernetes Computer,
MCP, Lore, storage recovery or model acceptance. Images must be immutable Linux
amd64 artifacts and actual private inputs remain outside Git. Normal runtime adds,
removes, routes, grants and provisioning defaults use admitted live APIs, not Helm
inventories or Hub restarts. See the canonical
[architecture](https://github.com/VeoveoAI/veoveo-docs/blob/main/LORE_OPENSHELL_INTEGRATION.md)
and [execution plan](https://github.com/VeoveoAI/veoveo-docs/blob/main/OPENSHELL_HARDCUT_PLAN.md).

## Historical pre-Kubernetes deployment and receipts

Everything below is preserved historical evidence, not a current Linux launch
procedure or a claim that the new Kubernetes placement has passed. Old source pins,
host routes and Compose commands must not select the replacement runtime.

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

The reusable application PostgreSQL image adds pgvector 0.8.7 and PostGIS 3.6.4.
Follow its [build, existing-database enablement and service-role checks](postgres/README.md);
these additions preserve the current service/schema ownership. Source preparation
is not a runtime qualification receipt.

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

[The object API configuration rule](openshell/bioma/cloudflare-object-api.json)
selects Cloudflare's native `http_config_settings` override: `bic=false` only for
`veoveo-objects.bioma.ai`. Signed S3 transfers are non-browser traffic; origin
signatures, verified TLS and all other hosts/security settings remain in force.
Apply/read back through the existing operator Rulesets API as described in the
[reference procedure](openshell/REFERENCE.md#cloudflare-object-api-setting-bioma-selection).
The rule is applied and read back; global Browser Integrity Check remains on.
Default Python and curl signed transfers pass with exact bytes/hash/PNG, while
unsigned and tampered signatures retain origin 403 refusals. No UA override, TLS
bypass or proxy was used. No browser impersonation is an installation step.

| Component | Selected source revision |
| --- | --- |
| OpenShell | `6589a918a7a84640969f9f77b852695e210d713f` |
| Hub | `ed6778f6a7e61df4f4c42241a589d9450f2bd63f` |
| Time | `d70ac8e2f9bdfb1c012ee744e5cd119ce4bca1dd` |
| Artifact | `00c8e93f5ca3ffe9137773754a4945c6d349b3bf` |
| Media | `4e8504b2c9bc72b0b249a8cf122e29983634d2e8` |

The selected Time metadata follow-up is published, gated and deployed; its new
seven-case baseline passes in 14.84 seconds. Earlier baseline/recovery receipts
below retain their historical `e607b2e` source.

Build through each component's existing procedure and select its resulting immutable
image in native OpenShell. These pins do not claim registry publication. Exact local
image identities and runtime receipts belong in the
[execution checklist](https://github.com/VeoveoAI/veoveo-docs/blob/main/OPENSHELL_HARDCUT_PLAN.md#reference-linux-deployment-and-signed-wavespeed-webhook-goal).

## Qualification status

Remote access is restored. All seven baseline source repositories are published
and pass their component gates both on Mac (Linux ARM64 containers) and on the
actual Linux x86_64 host: Core `433ed5f`, SDK `b0b8d86`, Hub `ed6778f`, Time
`e607b2e`, Artifact `00c8e93`, Media `4e8504b` and MCP template `b39a604`.
Matching runtime builds pass, and all four fresh native application sandboxes plus
the synthetic provider fixture are Ready at those baseline revisions.
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
bounded MiMo qualification now passes the complete scenario; the three timed-out
attempts below are historical and all used the real Artifact retrieval scenario. Earlier frozen-source
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

The first two bounded OpenCode/MiMo attempts used explicit Build and
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
release (8.599 ms cleanup). The third, observed 600-second attempt also timed out:
07:08:38.339632–07:18:39.833546 UTC, 600.001049 seconds model phase, 601.463073
seconds total. It counted 1,624 reasoning deltas / 61,086 characters without tools,
finalized accounting or output; native interruption took 37.617 ms and released
its claim with zero resumes. Source review finds default reasoning omitted and
an output allowance up to 131,072 tokens, not an eight-step reasoning budget.
A new same-model `#none` candidate selects the native supported non-thinking
toggle while retaining all scenario/permission/Tasks boundaries. Local capture
passes: exact `reasoning.enabled=false`, identical 12 local tool schemas and two
intentional refusals with released claims, no inference. The first `#none` run
ended unsuccessfully at eight steps after 65.823 seconds: two local naming/search
errors and read-only resource discovery, without an intended MCP operation or file.
An actual-project localhost refusal probe then measured normal asynchronous inventory
growth from 12 to 50 tools in 101 ms, including the required direct MCP tools and
excluding generation. The corrected prompt separates direct MCP calls from Code Mode
resource helpers. Its same-model 16-step / 600-second run was partial:
2026-10-19 07:40:44.824397–07:43:29.677098 UTC, 164.850767 seconds total /
163.212114 seconds model phase, session `ses_eace4ea38ffeCdYeXWcDCUKj8w`.
The retained download verifies as an 883,996-byte PNG, 1024 × 1024 RGB, SHA-256
`007af757d14221e544098adc5a1e37488f7e57818c85c9e3d91e97587d646b96`.
The single Time schedule call was rejected for a missing `calendar-` ID prefix;
its published schema omitted that prefix/full local-date/time metadata. No Time
Task was created. Local Code Mode `.arrayBuffer()` / `crypto.subtle.digest` errors
preceded successful download. CLI exit 0 is not semantic acceptance. Durable session
cost is USD 0.0850859424; the 15-step CLI subtotal is incomplete. The Time metadata
fix is published at `d70ac8e` (tree `b4ac708`); both canonical Docker checks pass
141 tests / 10 skipped each, on Mac-hosted Linux ARM64 and actual Linux AMD64.
Matching runtime and QA rollout now pass the new seven-case Time baseline in
14.84 seconds. The live Hub catalog has 39 tools / 21 Time tools and exposes the
calendar prefix, 10–128-character bounds and full local-date/time metadata.
No new generation ran. The later 16-step / 600-second same-model run also failed
semantic acceptance (CLI exit 0): session `ses_eacc6751cffe60j73RL4fVYA1X`,
424.697897 seconds model phase / 425.959552 seconds total. Default Python signed
GETs received HTTP 403 / body code 1010 before expiry. A browser-like User-Agent
case eventually network-downloaded the exact 883,996-byte Artifact, not a local
copy, but the model made no Time resolution or schedule call. No Time Task was
created. At that checkpoint deterministic/recovery gates passed while final client
acceptance remained open.
The object-host-only native Browser Integrity Check rule above is applied and
qualified: default Python/curl signed GETs return 200; unsigned AccessDenied and
tampered SignatureDoesNotMatch remain 403.

The final Time-first run now passes semantic acceptance: 2026-10-19
08:39:08.179348–08:40:43.145956 UTC, 94.966864 seconds total / 92.797675 seconds
model phase, using the same exact MiMo `#none` variant, 16-step / 600-second bounds
and its own OAuth grant. All eight tool envelopes completed without errors: two
native time resolutions, exactly one completed Time Task with one occurrence,
one filtered Flux catalog match, retained Artifact discovery/provenance, one signed
download request and one native shell network download. The fresh exclusive 0600
file is the exact 883,996-byte PNG, with unchanged signed URL/method/headers and
no UA override, TLS bypass or local copy. Durable session cost is USD 0.0223635068
(41,621 input / 4,080 output / 254,688 cache-read / zero reasoning tokens); its
claim is released with zero resumes. No generation or new Media Task ran. The
[dated final receipt](https://github.com/VeoveoAI/veoveo-docs/blob/main/OPENSHELL_HARDCUT_PLAN.md#linux-final-time-first-opencode-mimo-receipt--2026-10-19)
records authoritative Task reconciliation and proof limits. This closes the final
client gate; the earlier failed attempts remain historical. No live push-versus-poll
or capability-body wire claim is made. No second paid generation was needed.
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
