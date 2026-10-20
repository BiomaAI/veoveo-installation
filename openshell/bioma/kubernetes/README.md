# Bioma Linux Kubernetes selections

Current placement is Linux x86_64 K3s, not the former host Docker/Compose runtime.
This source branch imports reusable template
`dd824156c1bcb9eb7c34e22b70781cec8587ebc2`, with reviewed follow-ups through
`94c7ff08f661e0365d949909ab64dc5cfd7afe2f`; the old files directly under
`openshell/bioma/` remain unchanged historical selections. Current Kubernetes
application qualification is in progress; the dated checkpoint below separates
measured cases from pending gates. Do not infer it from earlier Docker receipts.
Mac native development/test fixtures remain in the generic template.

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
| OpenShell | Maintained source b849a25c (chart/runtime base 846de5fa) and `kubernetes/openshell.values.yaml` plus `openshell.values.yaml` here |
| Native Lore | `kubernetes/lore.yaml` and `lore.toml` here; current reviewed image recorded below |
| Existing tunnel | `tunnel.yaml` plus native remote API body `cloudflared-ingress.json` here |
| Hub bootstrap fragment | `hub.example.json` here, merged into complete private trusted configuration |
| Native policies | `policies/` here; exact methods/binaries/provider bindings retained |
| Native discovery bootstrap | `bootstrap.json` here |

The immutable Linux image/source selections are recorded in the dated checkpoint
below. The current gateway includes destination-CA staging through `0299a1ec`;
future supervisor generations select Service-DNS fix `b849a25c`, while the unchanged
sandbox runtime remains from base `846de5fa`. A previously running supervisor may
retain its earlier generation image and roots; selecting new defaults does not
implicitly restart it. The Postgres extension image is verified 18.6 with UID/GID
999:999. Do not use the old host-gateway, superseded UID-1000 Computer images or
historical component-lock receipts as current runtime selections. The committed
bootstrap values are combined with the reviewed private image/identity overrides;
reapplying an old bootstrap digest is not a qualification or update procedure.

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

The native Kubernetes destination-CA input requires the complete gateway fix
through `0299a1ec1e9f8305ebfe967c2b033f36ecc7ba18`, now selected in the reference
deployment; native Service-DNS resolution requires supervisor `b849a25c`. The public ConfigMap is `openshell/platform-destination-roots-v1`,
key `ca.crt`, with gateway mount `/etc/openshell/platform-ca`. The generic values
select `additional_ca_bundle=/etc/openshell/platform-ca/ca.crt`. It contains only
the current public gateway, Lore and Seaweed roots. A workload-only CA mount is
not supervisor trust. Keep the database CA mount when composing private Helm
volume overrides. This source update neither selects a new image digest nor
changes running supervisor generations.


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

Private-registry image rows use prefix
`registry.cloudflare.com/cd9522254303bfb3d2322a0d9b82764f/`:

| Component | Actual source | Immutable image after that prefix |
| --- | --- | --- |
| Gateway | `0299a1ec1e9f8305ebfe967c2b033f36ecc7ba18` | `gateway@sha256:add687d9afe99a841db1511ff4c906a297c623b98f1228b8e85ef4429061123a` |
| Supervisor, new generations | `b849a25c79177e9306c52a93de82d9dfc879cb92` | `supervisor@sha256:07e639e0d292f0a6d77417a711465b1d06ef595f9fc34e3f067b8aabacf28581` |
| Sandbox runtime | `846de5fa01234a22827915b3f4e5b9092367078b` | `openshell/sandbox@sha256:5177d0c76e2119a09a3af290ebc1da625a1e9fdf3ddcad7485bc973585f1e9bf` |
| Hub | `9b83c26e9bdc926b054d089fd87ca26e3cba6f31` | `veoveo-hub@sha256:be9176ea306016a507fd358034d4630caac8c6a91a2f4a25807b251422b91638` |
| Time | `d70ac8e2f9bdfb1c012ee744e5cd119ce4bca1dd` | `veoveo-mcp-time@sha256:255c50ff5fd90e59cf76842ef8e3fcd21ace8ff0a15ca7f7fa1ec32ab5f796b3` |
| Artifact | `00c8e93f5ca3ffe9137773754a4945c6d349b3bf` | `veoveo-mcp-artifact@sha256:06ebc0f44421f8308d27a773945644beaf51981a6d95e837dc5fdc77e10114ce` |
| Media | `4e8504b2c9bc72b0b249a8cf122e29983634d2e8` | `veoveo-mcp-media@sha256:d1aefc0567b1376336ca0f9e1404a77b7dd124b5bc5e4647ffaaa435a136c22a` |
| Synthetic Media provider | Same Media source | `veoveo-mcp-media-provider@sha256:398f86bbda316b6cd40b2a88c332fadc6fcc809ca53f91b713fb6322227080d4` |
| Lore | `6b7a0e598b8fbbaed82c777109135ddb25873bbf` | `veoveo-lore@sha256:5bb1e4ebdbbfca67e8b265532dd9897f9ea33366f26a1b945d81eb9a7320cb6c` |
| Factory | Installation `d9f6bf59b9e0fe908c661701a6313cb8abc15c80` | `veoveo-factory@sha256:89e70eac86d2ea3a3dc1a245942b5535cda768cd2bb4f0d36f8add85378a98e5` |
| Computer | Same installation; OpenCode `4bd4891e9e3d67460eb43dcfcdefb5172c1279ff` | `veoveo-computer@sha256:5263868037398bfcfb8401cbf898d2a556f7c90d88c0b8f57588cd5131b82b1f` |
| PostgreSQL extensions | PostgreSQL18.6/vector0.8.7/PostGIS3.6.4 | `veoveo-postgres:18.6-vector0.8.7-postgis3.6.4-k3s@sha256:feacb84577fdca909cd0e3306784f9af84d083222dab00421244a1376520c28a` |

The retained Hub supervisor is from the earlier matching base image
`openshell/supervisor@sha256:a033e574832c7e857eef7618281b663f0ae881c01286cae4f6ba976fcdce78be`;
this is not evidence that every existing runtime has adopted the new supervisor.
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

Media registered at 09:02:46.796 UTC and completed native provider startup status
checks at 09:02:47.046 UTC; its exact selected image is Ready with zero restarts.
This proves registration/startup connectivity, not a completed synthetic Task.
Media Kubernetes Task acceptance, remaining service recovery and final host reboot
checks are pending. The fixture is synthetic; historical real-provider
callbacks do not qualify its current Kubernetes path. Final bounded OpenCode
acceptance is also pending and must select only
`deepinfra/XiaomiMiMo/MiMo-V2.6-Pro` after deterministic/deployed gates; no paid
model call was made for this documentation checkpoint.

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
