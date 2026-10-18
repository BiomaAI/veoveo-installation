# Native Media preparation

This is source preparation for the [Media execution plan](../../veoveo-docs/OPENSHELL_HARDCUT_PLAN.md#media-native-integration-plan),
not deployed acceptance. Preserve the qualified Time/Artifact paths, existing
PostgreSQL/SeaweedFS data and registration keys. Endpoint/provider/placement
selection stays in this installation and uses the existing local Work Context;
there is no Media registry or fixed dev/stage/release environment hierarchy.

## Source and identity prerequisites

Media's production and fixture images must come from the same reviewed component
revision. Its SDK and Artifact pins must refer to published, tested revisions.
Use the component's ordinary targets, recording each resulting immutable image ID:

```sh
MEDIA_REVISION=0589cb6dc192f8734bd2e5d183160868d682a102
docker build --target check ../veoveo-mcp-media
docker build --target runtime --build-arg VERSION=0.1.0 \
  --build-arg REVISION="$MEDIA_REVISION" -t veoveo/media:native ../veoveo-mcp-media
docker build --target fake-provider --build-arg VERSION=0.1.0 \
  --build-arg REVISION="$MEDIA_REVISION" -t veoveo/media-provider:native ../veoveo-mcp-media
```

Set `MEDIA_REVISION` to the reviewed commit before these commands. Inspect the
runtime labels and retain exact `MEDIA_RUNTIME_IMAGE_ID` and
`MEDIA_PROVIDER_IMAGE_ID` values for native creation. The fixture's `testing`
feature is enabled only in its separate build; production Media does not serve a
test build. Build qualification is separate from native deployment qualification.

REST registration/token exchange and MCP calls share the Hub origin through
nonoverlapping endpoint paths. This depends on the reviewed OpenShell source
`6589a918a7a84640969f9f77b852695e210d713f`, selected through the existing
[supervisor build workflow](README.md#build-and-provision). Verify actual policy
admission and the selected supervisor image before service creation. The gateway's
incremental policy-merge RPC also owns admission logic; changing its supervisor
image alone does not replace the stock gateway's merge implementation. Adopt and
verify the reviewed native gateway build as well before using incremental updates. Keep ambiguous
REST/MCP overlaps rejected and preserve MCP inspection, verified TLS and credential
bindings. A generic REST rule over `/mcp/local` is not an alternative.

After [Hub/Time preparation](HUB_TIME.md) and [private Artifact setup](ARTIFACT.md),
run the trusted identity/catalog helper:

```sh
./identity/configure-hub \
  --hub-origin https://vv-control--hub--http.openshell.localhost:17670 \
  --include-artifact --include-media
```

The helper adds only the reviewed private binding
`http://media.internal:8802/media/mcp` → `vv-services/media:8802`. Ordinary reruns
retain selected Time, Artifact and Media bindings; foreign placements fail for
review. Media requires selected Artifact. Existing keys, registration secret and
IdP client secrets/subjects persist. Existing Work Context output owner, policy and
membership constraints are retained; an ambiguous contributor membership fails.

Only selected/retained Media adds `vv-hub-billed`: its Hub role grants read/write
with the `billed` risk, without sensitive, destructive, physical or administer
risks. It uses the existing external IdP/client-credentials claims, local profile
and contributor membership alongside member/admin. The ordinary member receives
no billed grant. Dedicated clients receive no OpenShell realm authority; the
existing forwarder's service-workspace authority is unchanged. There is no new
server-permission registry: registered requirements and ordinary role evaluation
still decide the permitted calls.

Privately copy the generated `hub.json` into the existing `vv-hub-config` volume.
Hub captures native placements at startup, so activate it through native stop/start
and verify the same public key, external origin and Time/Artifact calls afterward.
Keep its management provider and other config/state volumes unchanged. Do not
replace the live file or restart anything as part of running this helper.

## Service credential custody and volumes

Inspect definitions before native creation; reuse matching owned state and refuse
foreign/conflicting resources. Import registration material from trusted Hub state
in a subshell, never a token argument:

```sh
(
  set -a
  . ./state/openshell/hub/hub.env
  set +a
  openshell profile import --workspace vv-services --file openshell/providers/media-registration.yaml
  openshell provider create --workspace vv-services --name vv-media-registration \
    --type vv-media-registration --credential VEOVEO_REGISTRATION_SECRET
)
(
  export MEDIA_PROVIDER_API_KEY=fake-generation-key
  openshell profile import --workspace vv-services --file openshell/providers/media-generation.yaml
  openshell provider create --workspace vv-services --name vv-media-generation \
    --type vv-media-generation --credential MEDIA_PROVIDER_API_KEY
)
```

The latter value is a public fake-provider fixture credential, not a real billed
provider key. Media receives only native opaque references. Its registration
reference is bound to POST `/oauth/register`; the generation reference is bound
only to the fixture's `/api/v3/**` bearer requests. Output GETs have a separate
unbound path. Media's own signing key signs SDK delegation assertions; it receives
no Artifact credential or S3 signing key.

Prepare the required fake webhook HMAC secret once in ignored
`state/openshell/media/provider.env`, directory 0700/file 0600. It contains only
`MEDIA_PROVIDER_WEBHOOK_SECRET`, generated privately by the trusted operator.
Preserve an existing value. Although this slice sends no webhooks, both binaries
require the configuration. Copy only this file into `vv-media-config` privately,
readable by UID 10001; never print it, put it on command arguments or copy the
whole operator state directory.

Use only native workspace-labelled named volumes:

```sh
docker volume create --label openshell.ai/sandbox-attachable=true \
  --label openshell.ai/sandbox-attachable-workspace=vv-services vv-media-state
docker volume create --label openshell.ai/sandbox-attachable=true \
  --label openshell.ai/sandbox-attachable-workspace=vv-services vv-media-config
```

Inspect labels and contents first. Inventory the legacy Media key and migration
checksums before generating another key or changing schema state. If a key exists,
adopt only `keys/server-key.p8` into `vv-media-state`, preserving its public identity,
mode 0600 and UID 10001 ownership. The writable state survives sandbox replacement.
Configuration is directory 0700/file 0600 and mounted read-only by
[Media](media-mounts.json) and [the fixture](media-provider-mounts.json). Neither
mounts operator directories, host binds or Docker sockets. The approved driver
configuration keeps resource admission enabled and bind mounts disabled;
`allow_driver_config` also admits validated tmpfs/CDI requests, but these specs use
neither.

## Native fixture and private service

Start the separate fixture first, with an explicit expected origin. These commands
use standard native lifecycle only; inspect existing same-name resources before
creation, and never replace unknown workloads:

```sh
openshell sandbox create --workspace vv-services --name media-provider \
  --from "$MEDIA_PROVIDER_IMAGE_ID" --policy openshell/media-provider.yaml \
  --no-auto-providers --driver-config-json "$(cat openshell/media-provider-mounts.json)" \
  --restart-policy on-failure --detach \
  --env MEDIA_FAKE_PROVIDER_LISTEN=127.0.0.1:8803 \
  --env MEDIA_FAKE_PROVIDER_ADVERTISED_BASE=https://vv-services--media-provider--http.openshell.localhost:17670 -- \
  /bin/sh -c 'set -a; . /etc/veoveo/media/provider.env; set +a; exec /usr/local/bin/veoveo-mcp-media-fake-provider'
openshell service expose --workspace vv-services media-provider 8803 http \
  --authorization-mode bearer-passthrough
```

Require the returned exposure origin to equal the configured advertised origin
exactly. The gateway remains loopback-bound with HTTPS and normal hostname/CA
verification. This exposure is for the test fixture only, preserving provider
Bearer semantics; it is not public Media MCP ingress. The fake's HTTP status/output
links must use that same origin, never its bind address or rewritten Host.
It has no outgoing network policy and makes no callback in status-check mode.

After PostgreSQL, SeaweedFS, Hub, Artifact and the fixture are ready:

```sh
openshell sandbox create --workspace vv-services --name media \
  --from "$MEDIA_RUNTIME_IMAGE_ID" --policy openshell/media.yaml \
  --provider vv-media-registration --provider vv-media-generation --no-auto-providers \
  --driver-config-json "$(cat openshell/media-mounts.json)" \
  --restart-policy on-failure --detach \
  --env VEOVEO_HUB_ISSUER=https://vv-control--hub--http.openshell.localhost:17670 \
  --env VEOVEO_PUBLIC_BASE_URL=http://media.internal:8802 \
  --env VEOVEO_PORT=8802 --env VEOVEO_KEY_DIRECTORY=/var/lib/veoveo/media/keys \
  --env MEDIA_PROVIDER_URL=https://vv-services--media-provider--http.openshell.localhost:17670 -- \
  /bin/sh -c 'set -a; . /etc/veoveo/media/provider.env; set +a; exec /usr/local/bin/veoveo-mcp-media'
```

Keep `VEOVEO_PUBLIC_ORIGIN` unset. No Media service exposure is created: Hub reaches
its logical endpoint over authenticated native ForwardTcp. [Media's policy](media.yaml)
separates registration, metadata/JWKS, `/oauth/token`, and `/mcp/local` Artifact
calls. The SDK upload path requires create/sign-parts/complete/abort tools,
resource reads and subscriptions for verification; it uses modern MCP inspection.
PostgreSQL and signed S3 bytes use TCP on ports 5432 and 9000, respectively.
Verify `host.openshell.internal:9000` from each byte client without changing signed
authority/headers; the [Mac resolution prerequisite](ARTIFACT.md#trusted-preparation)
still applies to the final host-client qualification.

## Trusted acceptance preparation

Use a separate trusted workspace such as `vv-media-qa`. Import
[the member/billed profile](providers/media-qualification.yaml) there and create
`vv-media-qualification --runtime-credentials` with the standard native provider
commands from [Hub/Time setup](HUB_TIME.md#native-providers-and-workspace-authority).
Configure two independent refresh entries before creating a runner:

| Credential key | Trusted refresh input | Actual client |
|---|---|---|
| `HUB_MEMBER_REFERENCE` | `member.refresh.env`, `VV_HUB_MEMBER_CLIENT_ID` / `VV_HUB_MEMBER_CLIENT_SECRET` | `vv-hub-member` |
| `HUB_ADMIN_REFERENCE` | `billed.refresh.env`, `VV_HUB_BILLED_CLIENT_ID` / `VV_HUB_BILLED_CLIENT_SECRET` | `vv-hub-billed` |

Use `--secret-material-env client_secret=...` for each secret and rotate each entry
once for provisioning. Keep refresh material in native custody; never mount those
files. `HUB_ADMIN_REFERENCE` is only the existing acceptance role selector here;
it must not receive `vv-hub-admin` credentials. One explicit provider binding
selects either distinct supplied opaque reference without substituting identities.
Do not attach this qualification profile to author factories or the Media service.

Compile the component-owned acceptance executable from the reviewed source with
`--features testing --test acceptance --no-run` in its dev image. Transfer only the
reviewed executable to `/sandbox/bin/media-acceptance` in the trusted runner and
use [its narrow policy](media-qualification.yaml). The runner holds no management
credential or restart authority. It admits `media__run` for both identities so the
ordinary member's request reaches Hub's billed-permission refusal. Successful
catalog/schema/run, Task get/cancel, resource/subscription and Artifact download
requests must produce actual application outcomes; native transport errors prove
no Hub refusal. The disjoint GET own-usage rule supports the retained separate
real-provider acceptance case, not permission to bill that provider now.

```sh
export VEOVEO_ACCEPTANCE_HUB=https://vv-control--hub--http.openshell.localhost:17670
export VEOVEO_ACCEPTANCE_MEMBER_BEARER_ENV=HUB_MEMBER_REFERENCE
export VEOVEO_ACCEPTANCE_ADMIN_BEARER_ENV=HUB_ADMIN_REFERENCE
/sandbox/bin/media-acceptance --ignored --skip real_provider --nocapture --test-threads=1
```

Only the two existing fake-provider cases run here. Additional deployed lifecycle
proofs remain pending: independent request evidence for no resubmission, actual
cancellation, externally orchestrated in-flight recovery, retained bytes/metadata,
provenance, usage and renewal. The standalone fake has no component-counter API;
a single stored output is not evidence of one submission. Add no test-control API
without review. Keep the fixture running across a Media restart when testing
provider-operation recovery. Inspect actual provider refresh application and leave
measured margin before the next native credential fence; do not retry mutations or
hide interrupted calls. Record same persisted public keys separately from generated
registration client IDs, which may change at restart.

OpenCode with explicit `deepinfra/XiaomiMiMo/MiMo-V2.6-Pro` is the last bounded
qualification only after deterministic/unit/integration/deployed probes pass.
Preflight its actual Task interoperation without model calls first. No real billed
provider, public webhook, generic environment composition or Media Lore/factory
qualification is claimed by these templates.
