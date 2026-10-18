# Native reference installation with Entra

This prepares the reference Linux goal in the
[execution plan](../../veoveo-docs/OPENSHELL_HARDCUT_PLAN.md#reference-linux-deployment-and-signed-wavespeed-webhook-goal).
It is configuration, not a qualification receipt or deployment controller. Public
origins below are examples; use the operator's reviewed DNS/TLS configuration in
private state. Preserve remote source, databases, S3 data, signing keys, native
credential state and backups before replacing workloads. GPU/CUDA is separate.

Use the existing Docker-driver gateway, providers, policies, volumes and lifecycle.
Do not run the local Keycloak profile or identity HTTPS edge on this Entra reference.
The Mac's existing setup remains unchanged. Hub requires Tasks and clients must
implement the supported MCP specification; add no taskless fallback.

## Entra and the two token relationships

OpenShell authenticates Entra access tokens directly. The gateway's issuer,
audience, roles and scopes must match independently verified tokens for its own
resource. Start from [the native gateway example](entra-gateway.example.toml).
Use `roles_claim = "roles"` and `scopes_claim = "roles"` when application roles
carry the required native permissions. Do not disable role/scope enforcement
because an app-only token has no delegated `scp` claim.

The operator needs `openshell-admin` and `openshell:all`. The separate forwarder
needs only `openshell-user` and `sandbox:write`; add its actual validated token
`sub` as a **user** in `vv-services` only. Do not substitute Entra `oid` for this
native membership key, share the operator identity, or assign the forwarder an
admin role. App roles and their user/application assignments are Entra operator
configuration; possessing a client secret does not prove those grants. Configure
the selected resource's v2 access-token version and exact audience, then verify
issuer, audience, roles, expiry and native admission before deployment.

Register the native CLI with its exact gateway URL, tenant-specific issuer,
client ID and selected resource scopes using `openshell gateway add ...
--oidc-issuer ... --oidc-client-id ... --oidc-scopes ...`. The reference qualified
native device authorization with a separate Entra public CLI registration
(`isFallbackPublicClient = true`): request the resource's `access_as_user` scope
plus `openid profile offline_access`, then run:

```sh
OPENSHELL_NO_BROWSER=1 openshell gateway login <name>
```

The browser authorization-code flow uses PKCE, state and an HTTP loopback callback;
it requires an exact provider-supported redirect registration. A random-port
`127.0.0.1` callback was not qualified by this reference device-flow receipt.
Trusted client-credentials login instead reads `OPENSHELL_OIDC_CLIENT_SECRET` from the
operator environment; never put it on argv. Select `<resource-App-ID-URI>/.default`
for app-only tokens. This is distinct from the JWT's `aud` value. No client mTLS
identity is required for these OIDC users; ordinary server TLS verification and
native supervisor/control certificates remain required.

Hub application clients use its existing OIDC code broker. Entra authenticates
the user; Hub issues the normal application access/refresh grant, including its
Work Context authority. A plain Entra access token is not substituted for Hub's
RFC 9068 profile bearer. The Entra confidential Web registration must include
`https://veoveo.example.com/oauth/callback`; the secret is held only by trusted
Hub, not by the agent. Hub checks signature, issuer, application audience and
nonce, maps `oid` to the stable subject and maps only the selected `tid` to the
installation tenant. Sign-in alone grants no Work Context or permission.

## Prepare existing Hub schemas

Privately supply `VEOVEO_IDP_OIDC_TENANT_ID`, `VEOVEO_IDP_OIDC_CLIENT_ID`,
`VEOVEO_IDP_OIDC_ISSUER`, `VEOVEO_IDP_OIDC_CLIENT_SECRET` and the existing trusted
`VEOVEO_DATABASE_PASSWORD`. Save the verified issuer's standard OIDC discovery
JSON privately; preparation does not fetch it or mutate Entra. Review its issuer,
JWKS and authorization/token endpoints. Public example UUIDs in
[entra.example.json](../identity/entra.example.json) are deliberately unenrolled.

From the separate reference installation checkout, run the existing helper:

```sh
./identity/configure-hub --identity-provider entra \
  --hub-origin https://veoveo.example.com \
  --oidc-discovery-file /operator/private/entra-discovery.json \
  --native-gateway https://host.openshell.internal:17670 \
  --tenant reference --work-context reference-work --policy-version reference-policy \
  --owner-object-id '<administrator-object-id>' \
  --admin-object-id '<administrator-object-id>' \
  --member-object-id '<ordinary-member-object-id>' \
  --billed-object-id '<billed-test-user-object-id>' \
  --application-client-id opencode \
  --client-redirect-uri http://127.0.0.1:3210/callback \
  --include-artifact --include-media
```

Use the actual application's supported exact callback; the loopback example is not
an assertion that every client uses that port/path. Member/admin/billed selectors
are explicit stable Entra object IDs, never display names. Their installation
roles select declared access/risk; billed grants only `billed`, not administrative
or destructive risk. The selected administrator owns output policy. Work Context
membership lists principals, not the shared public application client, so another
tenant user cannot gain membership merely by logging in. A single identity given
admin authority cannot also prove the ordinary-member denial case.

The helper performs no identity-administration, database, provider or deployment
operation. It writes only standard owner-only component files under ignored
`state/openshell/hub/`: `hub.json`, `hub.env` and the public
`authorization-server.jwks.json`. Hub's own application signing key, forwarded
identity key, audit/refresh keys and registration secret persist across reruns;
no caller signing keys are generated. The Entra secret is copied only into trusted
Hub's private environment. Validate the generated catalog using the component CLI:

```sh
veoveo-hub validate --config state/openshell/hub/hub.json
```

Reruns retain selected private Time/Artifact/Media bindings and policy definitions.
Changed issuer, clients, principal grants, tenant/context, owner, keys or native
control endpoint require separate reviewed migration/recovery; the helper refuses
to reconcile them silently. Never point the reference helper at Mac private state.
Public application origin and private native control endpoint are distinct inputs.
Hub still captures placement at startup; preserve the existing native service
coordinates and mount/lifecycle procedures from [Hub/Time](HUB_TIME.md),
[Artifact](ARTIFACT.md) and [Media](MEDIA.md), rather than adding a launcher.

## Native custody and exact policy

Adapt [Hub's Entra policy](hub-entra.example.yaml) to the verified discovery
endpoint paths. It admits only Hub's executable, public JWKS GET and token POST,
plus its existing private ForwardTcp and database endpoints. It needs no Keycloak
administration or JWKS alias. Compare actual native exposure and public routing
before using the public origin; these templates create neither route.

Import [the forwarder profile](providers/entra-hub-forwarder.example.yaml) only
after selecting its exact tenant/token URL, resource scope and dedicated client.
Use existing `provider refresh configure --strategy oauth2-client-credentials`
with public `client_id` material and `--secret-material-env` for `client_secret`.
Attach only its opaque management reference to Hub and only the ForwardTcp policy.
Native custody owns refresh; no token worker is required.

After the agent's ordinary Hub PKCE login, its Hub refresh grant can use the
[native application profile](providers/entra-hub-application.example.yaml):
`oauth2_refresh_token`, the selected public client ID and protected `refresh_token`
material. Use `--secret-material-env`, never argv values. Bind the provider to the
exact Hub MCP endpoint in the existing client policy. For qualification, keep
member and billed sessions distinct; use their intended opaque references and
separate refresh entries. An Entra client secret is not a Hub client-credentials
grant. Fully unattended hosted Hub clients retain their existing `private_key_jwt`
contract and need a separately reviewed caller-custody decision.

Service registration uses the existing per-service initial-access providers.
Adapt the existing Time/Artifact/Media policies to the actual Hub HTTPS authority,
metadata, registration and token endpoints. Retain exact modern MCP rules and
binary restrictions; add no broad REST/MCP allow. Actual services stay private
under native ForwardTcp bindings. Media's signed callback uses its existing
`/media/operations/{operation_id}/{token}` route, public origin and signature
verifier; expose only that path through the reviewed existing tunnel. Verify
actual signed callback receipt and event completion separately from status polls.

## Native SeaweedFS HTTPS and signed authority

SeaweedFS remains trusted durable bootstrap. Its pinned 4.48 binary natively serves
S3 HTTPS: `s3.cert.file` and `s3.key.file` with `s3.port.https=0` serve TLS on the
selected `s3.port` itself. The existing bootstrap defaults stay HTTP for the Mac.
For the reference, privately set:

```sh
VEOVEO_STORAGE_TLS_DIRECTORY=/operator/private/object-tls
VEOVEO_STORAGE_TLS_CERT_FILE=/etc/seaweedfs/tls/tls.crt
VEOVEO_STORAGE_TLS_KEY_FILE=/etc/seaweedfs/tls/tls.key
```

Use the standard [read-only TLS override](../compose.storage-tls.yaml) with the
existing Compose bootstrap. Inspect the source certificate/key and volume state
first; the bind refuses to create a missing source. Validate the combined files
before replacing only the existing SeaweedFS service. No certificate/key is copied
into an image, and no additional proxy is introduced. Keep administration and
storage signing credentials private; retain the dedicated bucket-scoped Artifact
identity and all data.

The existing tunnel's object-host route must use verified TLS to that native S3
listener, with a certificate valid for the selected origin server name. Preserve
the public S3 Host, method, path/query and headers; never rewrite a returned signed
URL. Configure Artifact's `VEOVEO_STORAGE_SIGNING_ENDPOINT` to
`https://objects.veoveo.example.com`. For initial qualification the same reachable
HTTPS authority may be used for `VEOVEO_STORAGE_ENDPOINT`; a distinct internal
endpoint requires its own verified route/trust. Artifact uses path-style S3, so
no wildcard bucket hostname or S3 adapter is needed. Native byte-transfer policies
must admit this exact authority/port for intended binaries while preserving SigV4.

Qualify an actual signed upload/download from both the Linux workload and the Mac,
unchanged method/URL/headers, exact bytes/hash, ranges where required and refused
bucket/IAM access. TLS configuration, successful rendering and a public DNS record
are not that acceptance. The public object route must not expose management
listeners; app registration and MCP stay behind Hub.
