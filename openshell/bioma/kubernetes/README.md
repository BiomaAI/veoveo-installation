# Bioma Linux Kubernetes selections

Current placement is Linux x86_64 K3s; the selected Kubernetes foundation and
application images are deployed. This source branch imports reusable template
`dd824156c1bcb9eb7c34e22b70781cec8587ebc2`, with reviewed follow-ups through
`94c7ff08f661e0365d949909ab64dc5cfd7afe2f`; files directly under `openshell/bioma/`
remain historical selections. A third coordinated full-host reboot recovered all
nine owned `restart_policy=always` services, Computers and QA sandboxes
automatically, with fresh runtime generations and all 25 PVC bindings retained.
The `never` Time QA runner remained stopped as expected; it was started later only
for its verifier. The selected gateway is now `53e36658` and the final bounded
OpenCode acceptance passed with the explicitly selected MiMo model. See the dated
checkpoint below for evidence, the earlier second-reboot failure, and the exact
boundaries of each result. Mac native development/test fixtures remain in the
generic template.

## Foundation inputs

Use the ordinary [foundation procedure](../../../kubernetes/README.md) and
[native workload bootstrap](../../../kubernetes/WORKLOADS.md), selecting these
public Bioma inputs where they replace generic placeholders:

| Input | Selected file/value |
| --- | --- |
| Node/CNI | `kubernetes/k3s.yaml`, `kubernetes/cilium.values.yaml` plus `cilium-node.values.yaml` |
| Agent Sandbox | `kubectl apply -k kubernetes/agent-sandbox` (official 1.0.6, amd64 digest) |
| CloudNativePG | Official chart 0.29.1/operator 1.30.1; `postgres.yaml` here |
| SeaweedFS | Official chart 4.48.0 and `kubernetes/seaweedfs.values.yaml` |
| OpenShell | Maintained source 53e36658 (runtime base 846de5fa) and `kubernetes/openshell.values.yaml` plus `openshell.values.yaml` here |
| Native Lore | `kubernetes/lore.yaml` and `lore.toml` here; current reviewed image recorded below |
| Existing tunnel | `tunnel.yaml` plus native remote API body `cloudflared-ingress.json` here |
| Hub bootstrap fragment | `hub.example.json` here, merged into complete private trusted configuration |
| Native policies | `policies/` here; exact methods/binaries/provider bindings retained |
| Native discovery bootstrap | `bootstrap.json` here |

The immutable Linux image/source selections are recorded in the dated checkpoint
below. Current gateway source `53e3665811a72dd1555edb18aeb4fedef4158dbd` includes
destination-CA staging, GPU propagation and admitted terminal-supervisor recovery;
selected supervisor source `d7a990083214e8a618f05b1b471aeeac6d9aa82a` includes
expired launch-bundle recovery. The unchanged sandbox runtime remains from base
`846de5fa`. Running generations adopted the selected supervisor on the coordinated
Starts before the third reboot. The Postgres extension image is verified 18.6 with
UID/GID 999:999. Do not use the old host-gateway or superseded UID-1000 Computer
images as current runtime selections. The committed `openshell.values.yaml` selects
the live immutable gateway, supervisor and runtime digests shown below.
Private database/identity inputs remain operator-owned; do not reintroduce stale
image overrides when composing them. Reapplying an old digest is not qualification.

```sh
helm upgrade --install cilium cilium/cilium --namespace kube-system \
  --version 1.20.3 -f kubernetes/cilium.values.yaml \
  -f openshell/bioma/kubernetes/cilium-node.values.yaml
kubectl apply -f openshell/bioma/kubernetes/postgres.yaml
helm upgrade --install openshell "$OPENSHELL_SOURCE/deploy/helm/openshell" \
  --namespace openshell -f kubernetes/openshell.values.yaml \
  -f openshell/bioma/kubernetes/openshell.values.yaml
```

These commands require the foundation's exact native private Secrets/public CAs
already prepared. They do not create application identities, credentials or grants.
The selected management audience/tenant are public metadata. Verify an actual
native token and exact required scopes; successful discovery alone is insufficient.
Hub's dedicated platform-admin identity needs `config:read` for GetGatewayInfo,
plus the existing six workspace/sandbox/provider permissions. No user Computer
receives this control identity. All native workload API mutations require the
ordinary separately authenticated operator/Hub identity.

## Public identity and private service transport

Public origins remain `https://veoveo.bioma.ai` and
`https://veoveo-objects.bioma.ai`. Entra is human/management authentication; Hub's
existing issuer owns explicit repository assignments/native tokens. No direct-IdP
repository helper, global grants or custom Lore authorization is restored.

Private endpoints are the maintained gateway Service on 8080, PostgreSQL RW Service
on 5432, SeaweedFS S3 Service on 9000 and Lore Service on 41337, as selected in the
normal Kubernetes inputs. Native supervisors resolve Service DNS. The S3 TLS leaf
covers both its Service DNS and public signing hostname; the Lore leaf covers
`lore.veoveo-system.svc.cluster.local`. Public-only trust files remain separate
from private CA keys. Private native storage.env/client URIs use end-to-end TLS
and PostgreSQL verify-full with the exact public-CA path. Generate managed-role
password files without surrounding whitespace or a terminal newline: CNPG 1.30.1
trims that whitespace before applying role passwords. The Secret and client
credential must match the resulting password; see the
[managed-role bootstrap contract](../../../kubernetes/README.md#postgresql-and-native-storage-identities).
Keep exact `Admin:artifacts` on the existing `veoveo-artifact` native actions
identity: Artifact always calls CreateBucket before its CORS/lifecycle setup,
and Seaweed4.48 checks bucket administration even when the bucket already exists.
Do not grant global `Admin`, IAM administration, other-bucket access, or add this
action to Lore. Keep native `Read:lore` and `Read:artifacts` in their respective existing S3
identities alongside object-scoped actions: HeadBucket needs bucket-root read,
not just object read or List. Do not rewrite signed object Host/path/query/headers.

The native Kubernetes destination-CA input, pending-supervisor classification and
terminal infrastructure-loss recovery are selected from gateway
`53e3665811a72dd1555edb18aeb4fedef4158dbd`; native Service-DNS resolution and
expired launch-bundle recovery are selected from supervisor
`d7a990083214e8a618f05b1b471aeeac6d9aa82a`. The public ConfigMap is
`openshell/platform-destination-roots-v1`,
key `ca.crt`, with gateway mount `/etc/openshell/platform-ca`. The generic values
select `additional_ca_bundle=/etc/openshell/platform-ca/ca.crt`. It contains only
the current public gateway, Lore and Seaweed roots. A workload-only CA mount is
not supervisor trust. Keep the database CA mount when composing private Helm
volume overrides. The selected image digests below include these fixes. Source
changes do not alter running generations; an explicit operator apply remains a
separate action.


The selected `tunnel.yaml` retains the existing **remotely managed** tunnel.
Create native Secret `public-tunnel` in `veoveo-system`, key `token`, from the
existing private tunnel token file. `cloudflared tunnel run --token-file` reads
that mounted file; no token appears in argv or environment. Do not assume a
`credentials.json` exists or create a new tunnel. Mount only public native gateway
and storage CAs in `public-tunnel-ca` ConfigMap (`gateway.crt`, `storage.crt`).

`cloudflared-ingress.json` is the ordinary native remote ingress API request body.
Using the existing operator account/tunnel identity from `../cloudflared.json`,
apply/read back through the existing Cloudflare API:

```text
PUT /accounts/{existing_account_id}/cfd_tunnel/{existing_tunnel_id}/configurations
body: openshell/bioma/kubernetes/cloudflared-ingress.json
```

Use private native curl configuration for existing API authentication; never put
credentials in the command or commit them. This is an explicit operator apply,
not a custom controller. The old tunnel selection remains unchanged in Git.
The new routes retain the exact signed Media callback path, Hub exposure Host
routing and public object authority. Only private origins/CA mount paths change
to Kubernetes Services. Keep public S3 Host untouched. Retain the existing
object-host-only Cloudflare API setting from `../cloudflare-object-api.json`.
No user-agent/TLS bypass, alternate issuer or new proxy. API apply/readback and
actual request routing remain deployment gates, not source proof.
The pinned cloudflared metrics listener exposes its native HTTP `/ready` probe
on Pod port 2000: Ready requires at least one active tunnel connection. No liveness
probe restarts the connector during a transient network interruption; no public
Service exposes its metrics port. This does not prove each origin application.

## Native runtime ownership

Create native workspaces and required provider custody first, verify the actual
managed namespace, then apply the existing approved configuration/public-CA PVCs
and one-time Jobs **in that namespace**. Mount trusted config read-only outside
`/sandbox`. There is no namespace copy controller or per-workspace Helm release.
The example gateway ID is `openshell`; measured managed namespaces are
`openshell-openshell-vv-control` and `openshell-openshell-vv-services`. Namespace
names remain derived installation data (`openshell-<gateway_id>-<workspace>`),
not a fixed native contract. Use `openshell workspace create --name NAME` and
verify the actual native namespace before admitting the corresponding PVCs/Jobs.
These source examples do not rename or restart an existing gateway.
Computer templates use automatic per-sandbox workspace PVCs, never a shared fixed
`/sandbox` claim. Default template/policy references are versioned native API data.

`hub.example.json` is a typed fragment, not a complete replacement catalog. Keep
actual signing/identity/settings/services and the separate native control reference
in private trusted input. Its real repository and principal assignment lists start
empty; native Lore create emits repository IDs, then existing authenticated Hub
live publication grants only explicit actual principals. Do not commit principal
grants or seed invented repository IDs. The retained reference Work Context is
`reference-work`; validate its explicit existing memberships/identity mapping in
the complete input. Entra OIDC client IDs/secret locators left as generic markers
must be resolved privately before native admission.

New/removed MCPs, provider/templates, factories, Computers, request destinations
and assignments use existing live APIs. Hub's active revision remains authoritative
on restart; installation files seed only an empty catalog. No Helm runtime
inventory, startup DAG, automatic mutation replay, unrelated rollout or implicit
Computer replacement. Preserve current state on rejected configuration; observe
reconnect/reconcile and drain behavior explicitly.

## Qualification checkpoint — 2026-10-20

These records describe Linux amd64 deployment and retained receipts, not a claim
that every application or recovery scenario passed. Component checks, deployed
probes and final model acceptance are separate. Source pins below identify
maintained VeoveoAI fork revisions, not upstream releases or reproducible builds.
OpenShell integration `53e3665811a72dd1555edb18aeb4fedef4158dbd` is published on the maintained fork's `main`.

Private-registry image rows use prefix
`registry.cloudflare.com/cd9522254303bfb3d2322a0d9b82764f/`:

| Component | Actual source | Immutable image after that prefix |
| --- | --- | --- |
| Gateway | `53e3665811a72dd1555edb18aeb4fedef4158dbd` | `gateway@sha256:1bdeade25a8239b7c385924915de59f520be3c48322f79ef4be62d7ce5801564` |
| Supervisor, new generations | `d7a990083214e8a618f05b1b471aeeac6d9aa82a` | `supervisor@sha256:f1d8f896daa08d85f8667a595c82544d93cbe73f2d16250387ab484ee5a286d2` |
| Sandbox runtime | `846de5fa01234a22827915b3f4e5b9092367078b` | `openshell/sandbox@sha256:5177d0c76e2119a09a3af290ebc1da625a1e9fdf3ddcad7485bc973585f1e9bf` |
| Hub | `9b83c26e9bdc926b054d089fd87ca26e3cba6f31` | `veoveo-hub@sha256:be9176ea306016a507fd358034d4630caac8c6a91a2f4a25807b251422b91638` |
| Time | `d70ac8e2f9bdfb1c012ee744e5cd119ce4bca1dd` | `veoveo-mcp-time@sha256:255c50ff5fd90e59cf76842ef8e3fcd21ace8ff0a15ca7f7fa1ec32ab5f796b3` |
| Artifact | `00c8e93f5ca3ffe9137773754a4945c6d349b3bf` | `veoveo-mcp-artifact@sha256:06ebc0f44421f8308d27a773945644beaf51981a6d95e837dc5fdc77e10114ce` |
| Media | `f01cdb0b772a87e20835f5b88be18910a7785e54` | `veoveo-mcp-media@sha256:2da66a129757e3d54e379bb8a34c2b15da8b768681cd00702229ec44d838a920` |
| Synthetic Media provider | `4e8504b2c9bc72b0b249a8cf122e29983634d2e8` | `veoveo-mcp-media-provider@sha256:398f86bbda316b6cd40b2a88c332fadc6fcc809ca53f91b713fb6322227080d4` |
| Lore | `6b7a0e598b8fbbaed82c777109135ddb25873bbf` | `veoveo-lore@sha256:5bb1e4ebdbbfca67e8b265532dd9897f9ea33366f26a1b945d81eb9a7320cb6c` |
| Factory | Installation `d9f6bf59b9e0fe908c661701a6313cb8abc15c80` | `veoveo-factory@sha256:89e70eac86d2ea3a3dc1a245942b5535cda768cd2bb4f0d36f8add85378a98e5` |
| Computer | Installation build input `d9f6bf59b9e0fe908c661701a6313cb8abc15c80`; OpenCode `ed62aad52c80ecdf4297310ce84305aff5717b7d` | `veoveo-computer@sha256:12c2ba83bd6f3dea715d1f8ab25ee20dd81dfb8145868f9a193f73cb4ce695d4` |
| PostgreSQL extensions | PostgreSQL18.6/vector0.8.7/PostGIS3.6.4 | `veoveo-postgres:18.6-vector0.8.7-postgis3.6.4-k3s@sha256:feacb84577fdca909cd0e3306784f9af84d083222dab00421244a1376520c28a` |

At the pre-first-reboot checkpoint, the retained Hub supervisor was from the
earlier matching base image
`openshell/supervisor@sha256:a033e574832c7e857eef7618281b663f0ae881c01286cae4f6ba976fcdce78be`.
Owned applications adopted selected supervisor `f1d8f896` on pre-second-reboot
Starts. Recovery after that reboot failed and is retained as historical evidence
below; the third reboot exercised the selected gateway and supervisor images.
The corrected Factory and Computer run UID/GID 10001 and retain private directory
permissions. Their earlier UID-1000 digests are superseded.

Foundation selections remain K3s `v1.36.5+k3s1`, Helm `v3.22.1`, Cilium `1.20.3`,
Agent Sandbox `v1.0.6` amd64 digest
`876f9621e0f0e168bcff13aa377880b75fd37e1c8712f2f249e8878c22d06ffd`,
and CloudNativePG chart `0.29.1`/operator `1.30.1` image
`ghcr.io/cloudnative-pg/cloudnative-pg:1.30.1@sha256:b0f9805bd5f98592e7320b5ea624dd10a7a6ef8e477df5650655c94f0b242497`.
SeaweedFS chart `4.48.0` selects
`chrislusf/seaweedfs:4.48@sha256:4e61d15fd35994cb1e43e1e553dff106794841fd9a99ade2fc8c8bfce4d7872d`;
the existing tunnel uses
`cloudflare/cloudflared:2026.10.1@sha256:3c0502d2da137286136b44f5b1d0d0be7030cc4833db9f53cff86beadad6cefa`.

Measured component checks: Hub's corrected Mac/Linux Docker gates each passed
231 tests with one skipped. Native CA/DNS focused tests and strict Clippy passed;
OpenShell b849 `mise run docs` passed in 6.291 seconds with zero errors/three
warnings. Upstream chart render/lint/API admission and immutable image pulls
passed. These results alone do not establish application behavior.

Measured deployed cases:

- Cilium ingress/egress deny/allow, CNPG extension/TLS access and scoped private/
  public S3 PUT/GET/DELETE/HEAD with cross-bucket denial. Seaweed CA filename/SAN,
  CNPG managed-password whitespace and scoped bucket-root actions were corrected
  as installation inputs; Artifact's own startup additionally requires exact
  `Admin:artifacts`, not global Admin. A Ready Pod was not used as a substitute
  for these backend operations.
- Two real owners created separate private Kubernetes Computers; web navigation,
  denied cross-owner route/filesystem access, distinct PVCs and native Stop/Start
  scratch/project/Lore-auth persistence passed. Live versioned defaults changed
  only future provisioning. Invalid configuration retained the working revision.
- Real native Lore login, explicit assignment, allowed/denied clone, withdrawal
  beyond cached token expiry and native refresh passed. Published immutable
  repository/revision fixtures remain for later recovery/model acceptance.
- An isolated Factory cloned that published revision, built the synthetic Rust
  fixture with Cargo `--offline --frozen --release` in 387 ms and printed
  `published-native-fixture-v1`. Executable SHA-256:
  `7c215988c81b403f1b45d4de67b03aa0b7279885a9ea00a1d796dc3662a0f9eb`.
  Automatic provider renewal followed by a fresh clone beyond original expiry
  plus JWT leeway passed in 107 ms. No OpenCode/model provider was attached.
  Native stop/delete removed only its disposable sandbox/template/provider/profile/
  workspace; existing unrelated pod identities remained unchanged. This is
  synthetic fixture output, not inference or cross-machine reproducibility.
- Missed-notification reconciliation adopted a published revision in the same
  temporary Hub process after its PostgreSQL notification path reconnected.
  Both Hub identities remained unchanged; this does not prove multi-host HA.
  An existing Time event subscription delivered a later notification across live
  publication: 9.75-second test, 12.381-second operator sequence.
- Time's seven routed cases passed in 10.21 seconds; Artifact's six passed in
  223.15 seconds, including 1-GiB multipart/range/release. This is deployed service
  acceptance, separate from component tests and any model-driven scenario.

Media's six serial synthetic deployed cases passed in 49.06 seconds using source
`f01cdb0b772a87e20835f5b88be18910a7785e54`; its matching QA image digest is
`sha256:a6ba2faddd3b3c6320538bbc64d0a37e0e01b001bd7f4e2201685b32428b0c0f`.
A separate in-flight Task survived scoped Hub and Media restarts in 112.42 seconds:
Task `gtr_Bz2Fxto2vKUNu5zlnEcA9IDtHVc5egJxIJKzTZZba_8`, prediction
`01a158cb17c37c71a192c2a62c4f4b52`, output 65,536 bytes with SHA-256
`c6ee57f09dbd4b0e5c6072ec59f2bbce2decf3ef9b1c695af802f26ae28931ce`.
The initial suite passed four of six cases. The corrections make duplicate run
recording tenant-safe and make the Artifact client reject a terminal failed upload
on retry. Media now admits the exact public signed-upload authority with TLS
passthrough. The original transfer error was not retained, so that past cause is
unmeasured; the fresh suite proves the corrected path. Media consumes Artifact
client `58f9fbd2ceab7f267144676284b62bf756945427`, now included in Artifact main
`9a535440d989e24021ae172f71f3f5c08aa2703b`; the deployed Artifact server remains
`00c8e93` and the fixture remains `4e8504b` with the unchanged images above.
These outputs are synthetic byte fixtures, not inference or valid media encoding.
The second full host reboot did not recover owned OpenShell workloads
automatically. At 11:14:26Z, kubelet reported generation-scoped sandbox and
supervisor bootstrap Secret mount failures (`object not registered`). The gateway
restarted after a transient PostgreSQL DNS lookup failure and was Ready by
11:15:06Z; it emitted sandbox suspension events at 11:14:51Z. The event ordering
is measured, but the causal relationship is not established. After that reboot,
the `restart_policy=always` workloads were `Stopped`/`Suspended`; the `never` Time
QA runner was also stopped, as expected for its policy. The failure was returned to
the coordinator and fixed in the maintained gateway lifecycle handling. Evidence:
Linux `/tmp/k3s-expired-bundle-reboot-20261020.json` (SHA-256
`68b9b30971494810dab9fac8ee6b7eedda7fcc34d824361f7170f313fedecff8`), and filtered
gateway warnings `/tmp/k3s-second-reboot-gateway-warnings-20261020.log` (SHA-256
`a208671de72f3cc4d8f2666883a64369b0344f386e5c0bf737e2dd328a9bb351`).

A third coordinated full-host reboot was requested at 12:13:32Z; SSH returned at
12:15:34Z and the recovery snapshot was captured at 12:17:04Z. The boot ID changed
from `0beca792-4f06-41a8-90c8-09b2852b185a` to
`5da92057-917b-411a-8539-3271c97d47c9`. Without manual sandbox Starts, all nine
owned `restart_policy=always` workloads (Hub, Time, Artifact, Media, the synthetic
Media provider, two Computers, and Artifact/Media QA) reached native `Ready` with
fresh runtime generations, restart count 1 and null exit codes. Both Computers and
both service QA sandboxes passed native `exec /bin/true`. All 25 PVC UIDs, phases
and volume bindings matched preboot. The `never` Time QA runner remained `Stopped`
with restart count 0 and was started only later to run its prepared verifier. The
Gateway had an initial transient PostgreSQL DNS failure, then recovered to Ready
automatically. Evidence: Linux
`/home/rozgo/.config/veoveo/k3s/evidence/openshell-gateway-53e-recovery-20261020/postboot.json`
(SHA-256 `7ff98cfe7ec82dab116615cd920fbb117e268c33f999e5858b1f7ef10212b128`).
The final public checks retained the same saved browser session and Hub control
revision. The saved session GET returned HTTP 200 in 145.9 ms; the terminal
WebSocket attach completed in 941 ms (3 frames, 66 output bytes), and public
control-plane GET returned HTTP 200 in 146.29 ms with the unchanged revision/hash.

The final bounded OpenCode qualification used agent `build` with the explicitly
selected `deepinfra/XiaomiMiMo/MiMo-V2.6-Pro` (session
`ses_ea69c1ad3ffeKqVD2BVH1CSrMt`). It lasted 81.283 seconds from persisted user
message to final assistant response, used seven provider turns under the 8-turn /
240-second limit, and cost `$0.0131970424`. The scenario inspected the member's
pinned Lore repository and source, called Time `resolve_time` twice, then expanded
`calendar-final-k3s` (UTC, daily 09:00–10:00 window, maximum four occurrences).
Time returned one correct occurrence and `truncated=false`. The final run's
OpenCode export records 24,202 input tokens, 2,151 output tokens, 697 reasoning
tokens and 86,784 cached-read tokens. Synchronous Time task
`01a15964-de30-7e62-90dc-78b8a7def7c2` completed `expand_schedule` successfully
in 12 ms; earlier matching task `01a1595d-d258-7060-8f2f-db7c667e8fcd` succeeded
in 70 ms. Both tasks were owned by the same member subject; neither created
asynchronous operation or step rows. The Linux task receipt is
`/home/rozgo/.config/veoveo/k3s/evidence/mimo-final-20261020/time-task-receipt.json`
(SHA-256 `5a4277b0c5a6ba6c1a25712f2a7f38a518693b566d15ea55ac4804ffe1d8f6d4`).
The filtered final session export is 71,277 bytes, SHA-256
`e5b3c595b87053ffa0979a961b0cb81ced33fd9ff8acbd016b92a84d10425f08`; all seven
reasoning content parts were removed while text/tool outcomes and timings were
retained. The export is stored under the private Linux qualification evidence
folder and at `/tmp/k3s-final-mimo-qualification-20261020/second-run.json` on Mac.

The first final-run shell attempt referenced unavailable `tools.shell`; tool
search corrected it without making an external call. An earlier native Lore
repository-info attempt had failed with `Not authenticated` because it used the
wrong operator `LORE_AUTH_PATH`; comparison with the Computer process identified
the image's configured `/sandbox/home/.config/lore/auth` store. Login and
repository-info were repeated using the configured store, and the actual browser
PTY command exited 0 with the expected repository/source hashes before final
model acceptance. No token was copied or new authorization path added.

The six-case log is retained in the QA workspace as
`/sandbox/.media-acceptance-f01cdb0-20261020.log` (2,522 bytes, SHA-256
`4a8d3c5b9ddbdfd35f652ca8c81394521aafe6b91b00623357e9dc6dd3ec0e47`).

Retained evidence: Linux `/tmp/k3s-foundation-20261019/` (including `destination-ca/`,
`native-dns-supervisor/`, `hub-reconcile/`, `computer-v2/`, `lore-computer/`),
`/tmp/k3s-native-factory-qualification-20261020/receipt.json` (SHA-256
`6114cad906958669fe0a83bfe5ac366ea4715cd8b6ddf7f3341a8fdaf7bbc0e0`)
and `lifecycle-receipt.json` there (SHA-256
`b25196557b81228475f84bc08234612b628e62931dbff47baa4d894f91cbeefe`).
Operator Mac `/tmp/k3s-live-admin-20261020/` contains live default/reconcile/
held-stream receipts. These metadata/evidence locations are not bootstrap inputs;
never commit private source artifacts or credential-bearing captures. The canonical
execution plan owns subsequent gate completion and final deployment status.
