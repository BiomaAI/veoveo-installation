# Bioma native selections

Hub, Artifact and Media qualification use the same native `vv-hub-qualification`
provider in their trusted qualification workspace. Its distinct
`HUB_MEMBER_REFERENCE` and `HUB_ADMIN_REFERENCE` credentials represent the ordinary
member and the administrator with billed permission, respectively. Media's positive
caller is not billed-only. Preserve each human grant in this single credential
custody owner; do not copy its rotating refresh token into a second provider.

The separate `media-qualification-profile.yaml` is retained as an example but is
unused by this deployment. `media-qualification.yaml` binds both its MCP and own-usage
REST endpoints to `vv-hub-qualification`; tool/path admission remains unchanged.

The inherited [Artifact storage policy](../artifact-storage-policy.json) applies
unchanged to this installation's `artifacts` bucket. Apply it through the existing
native `s3.policy` procedure in [Artifact preparation](../ARTIFACT.md#trusted-preparation),
keeping bootstrap administration and service signing credentials separate.

For Media's native HTTP service exposure, including the fake-provider ingress
baseline, the trusted mounted `/etc/veoveo/media/provider.env` explicitly selects
`VEOVEO_ALLOW_LOOPBACK_HOSTS=true`. Preserve its secret and other reviewed settings
when adding the literal, then native stop/start the existing `vv-services/media`
sandbox so the existing environment-file loader reads it. Media binds
`0.0.0.0:8802` inside its isolated network; native ingress forwards
`Host: 127.0.0.1:8802`. The setting admits only the SDK's loopback host names;
normal TLS, authentication and signature checks remain in force. Keep
`VEOVEO_PUBLIC_ORIGIN` unset for this fake/status-check baseline. The independent
real Events selection is described in the
[reference procedure](../REFERENCE.md#media-event-completion-and-callback-ingress).
