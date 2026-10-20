# Bioma Linux Kubernetes selections

Current placement is Linux x86_64 K3s, not the former host Docker/Compose runtime.
This source branch imports reusable template
`dd824156c1bcb9eb7c34e22b70781cec8587ebc2`, with reviewed follow-ups through
`94c7ff08f661e0365d949909ab64dc5cfd7afe2f`; the old files directly under
`openshell/bioma/` remain unchanged historical selections. Current Kubernetes
application acceptance is pending. Do not infer it from earlier Docker receipts.
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
| OpenShell | Maintained source 846de5fa and `kubernetes/openshell.values.yaml` plus `openshell.values.yaml` here |
| Native Lore | `kubernetes/lore.yaml` and `lore.toml` here, actual reviewed image selected later |
| Existing tunnel | `tunnel.yaml` plus native remote API body `cloudflared-ingress.json` here |
| Hub bootstrap fragment | `hub.example.json` here, merged into complete private trusted configuration |
| Native policies | `policies/` here; exact methods/binaries/provider bindings retained |
| Native discovery bootstrap | `bootstrap.json` here |

The selected gateway/supervisor/sandbox Linux images are immutable registry
artifacts built from `846de5fa01234a22827915b3f4e5b9092367078b`; builder independently
pulled each digest through K3s. The selected Postgres extension image is immutable,
verified 18.6 with UID/GID 999:999. Do not use the old host-gateway or component-lock
receipts as replacement runtime selection. Final Hub/MCP/Computer/Lore source and
image identities are selected only after the corresponding builder gates.
No unverified image digest is invented in this source.

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

The native Kubernetes destination-CA input requires gateway fix
`f39b1fee81891646b57441d15d0d6e3a0c890385`; selection of its validated image remains
builder-owned. The public ConfigMap is `openshell/platform-destination-roots-v1`,
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

## Qualification still required

Native render/admission and verified image pulls are not deployed application
acceptance. Prove private gRPC/TLS and signed S3 bytes, actual scoped storage
credentials, late/interrupted dependencies, fresh real sign-in, Computer web/API/
streaming and Stop/Start persistence, owner isolation, Hub/provider renewal and
native Lore access before final exact MiMo acceptance. Record targeted Pod UIDs/
process starts and unrelated workloads across dynamic changes. Final model calls
are coordinator-owned and use only `deepinfra/XiaomiMiMo/MiMo-V2.6-Pro` after the
other gates; no model calls are part of source integration.
