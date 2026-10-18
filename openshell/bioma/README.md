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
