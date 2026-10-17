# Installation identity

Local development uses persistent Keycloak. The remote Linux reference uses
Microsoft Entra ID. Installers may keep the bundled Keycloak service or configure
another OIDC provider; Gateway authorization, roles and resource tokens remain
Veoveo's responsibility. No Lore fork is involved.

## Persistent local Keycloak

After creating the installation CA and starting the Gateway as described in the
installation README, run from the installation root:

```sh
./identity/provision
./identity/configure-gateway
```

Provisioning enables `COMPOSE_PROFILES=keycloak` in the ignored `.env`. Keycloak
26.8.1 runs in production mode with a dedicated PostgreSQL 18.6 database, not the
in-memory test fixture. All three containers restart with Docker. The operator-owned external volume
`vv-local_vv-keycloak-db` survives container replacement and `compose down -v`.
Provisioning creates it explicitly and refuses to replace missing credentials when
this database already exists. Do not delete it when
resetting a component's development state.

| Purpose | Address |
|---|---|
| OIDC issuer | `https://auth.localhost:8443/realms/veoveo` |
| Account and password management | `https://auth.localhost:8443/realms/veoveo/account/` |
| Keycloak administration | `https://auth.localhost:8443/admin/` |
| Gateway browser entry | `https://gateway.localhost:8443/oauth/authorize` |
| Gateway OIDC callback | `https://gateway.localhost:8443/oauth/callback` |

The local browser and trusted Gateway resolve the same issuer hostname. macOS
resolves `*.localhost` to loopback; on Linux hosts without that behavior add
`127.0.0.1 auth.localhost gateway.localhost` to `/etc/hosts`. Containers resolve
these names through Docker's aliases for the TLS edge. `.localhost` bypasses the
outbound dependency proxy in trusted runtimes.

### macOS certificate trust

After generating the installation CA, install its public certificate once in the
current macOS user's login keychain with SSL trust. Run from the installation root:

```sh
security add-trusted-cert -r trustRoot -p ssl \
  -k "$HOME/Library/Keychains/login.keychain-db" tls/ca/ca.crt
```

macOS may request authorization for this one-time trust change. It uses the user
trust domain and does not require `sudo`. Only the public CA certificate enters the
keychain; its private signing key stays in the installation's protected state.

OpenShell's OIDC discovery, login and token refresh use native certificate roots.
Earlier installations trusted only the `auth.localhost` leaf certificate for the
browser, which left the CLI reporting `UnknownIssuer`. Trusting the installation
CA supplies the issuer chain the CLI needs. Existing leaf entries can remain.
The CA trust persists across terminals and reboots; ordinary OpenShell commands
need no `SSL_CERT_FILE` or `SSL_CERT_DIR` export. Remove any Veoveo-specific shell
override added for the earlier smoke setup.

To inspect existing entries, compare these SHA-256 fingerprints:

```sh
openssl x509 -in tls/ca/ca.crt -noout -fingerprint -sha256
security find-certificate -a -c "Veoveo local installation CA" -Z \
  "$HOME/Library/Keychains/login.keychain-db"
security dump-trust-settings
```

Preserve this CA across bootstrap reruns. Renew endpoint certificates under the
same CA before expiry and reload the affected TLS endpoints; that requires no new
root trust installation. A new CA requires installing its public certificate on
each client before switching endpoints. Linux clients use their platform's trust
store. An externally hosted issuer with a publicly trusted chain needs no local
Veoveo CA trust for its login endpoint.

### Local credentials

Initial user and administrator details live in `state/identity/credentials.json`,
mode 0600 inside a mode 0700 directory. The ordinary username is the host's login
name; the separate administrator appends `-admin`. Change their passwords in the
account/admin UI and keep them in your password manager. The admin's initial
password must be changed on first login. This file is an initial handoff, not a
password synchronization mechanism. Re-running provisioning preserves database
users and passwords. The temporary bootstrap service account and its container
environment credential are removed after setup.

The confidential `veoveo-gateway` client uses authorization code + S256 PKCE, an
exact callback URI, and no password or service-account grants. Human membership
uses the stable `sub`, not the username. No email or personal profile fields are
required. Imported users receive Keycloak's standard default roles for managing
their own account; Veoveo resource membership is granted separately. Validate the
actual account console as well as the Gateway flow: browser requests carry an
`Origin` header, and the console requires these account permissions.
The local browser client has an exact loopback callback at
`http://127.0.0.1:18555/callback`; it is an integration client, not a shipped UI.
The configuration helper writes the OIDC secret into the existing trusted
`gateway.env`, so the normal Gateway launch continues to work. It restarts a running
Gateway while retaining its process configuration.

Envoy binds the browser listener to `127.0.0.1:8443`. PostgreSQL, Keycloak HTTP and
its management port are unpublished. Database and Keycloak run as non-root, with
all capabilities dropped and no-new-privileges. The database owner has no
superuser/create-role/create-database privileges. Only the trusted Gateway gets
the confidential OIDC client secret. Coding containers receive no identity
credentials, runtime mounts or route to the identity network. Environment files,
private keys and provisioning state remain ignored and outside build contexts.
Envoy removes caller-supplied forwarding headers before adding the configured
HTTPS origin. Preserve that mutation order; removing those headers afterwards
causes Keycloak to reject the browser's token exchange with `Invalid origin`.

Back up the identity database independently of component databases. For example,
run `docker compose exec -T vv-keycloak-db pg_dump -U postgres -Fc keycloak` into an
owner-only file under `state/identity/`, then encrypt it before off-host storage.
It contains password hashes, signing keys and client credentials. Preserve the
installation CA and private provisioning credentials through the operator's
normal encrypted backup process too. Test restoration before relying on a backup.

## Installer choice and the Linux reference

Bundled Keycloak is a supported provider choice, not a required Veoveo dependency.
For a network installation, give Keycloak its own HTTPS hostname, adjust
`KC_HOSTNAME`, Envoy's hosts/certificate/forwarded headers, the Gateway's issuer,
client callback and identity configuration together. Keep the database and
management interface private. Use the provider's supported clustering and backup
configuration when the installation needs high availability. A local loopback
configuration is not a public production ingress configuration.

For Entra, omit the `keycloak` Compose profile and its three services. Start with
[entra.example.json](entra.example.json), a configuration fragment rather than a
complete Gateway installation. Replace `TENANT_ID`, `APPLICATION_CLIENT_ID`, the
installation origin, resource and tenant mapping; merge entries by ID into the
installation's Gateway configuration. Point the relevant profile and authorization
server's `identityProvider` to `entra`, enable `oidc_authorization_code_pkce`, and
configure the public Gateway authorization/token endpoints and client registration.
Grant roles explicitly to issuer + stable object ID principals; sign-in alone must
not confer installation membership.

Register a single-tenant confidential **Web** application in Entra with the exact
`https://veoveo.example.com/oauth/callback` redirect. Supply its credential only to
the trusted Gateway through its configured secret source. Use the tenant-specific
v2 issuer; do not use `common` or `organizations`. Permit the configured Entra
JWKS/token host through the trusted egress proxy and expose the Gateway's human
OAuth routes through the reference's authenticated HTTPS ingress. The current
callback/share-only tunnel does not expose those routes. Follow Microsoft's
[OIDC metadata](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc)
and [authorization code flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow)
documentation. Entra requires the reference tenant and app registration; this
local setup does not create those or modify the remote deployment.

## Desktop integration (pending retirement)

The user withdrew Desktop acceptance on 2026-10-17. The results below are historical,
and the adapter remains deployed only until the
[direct Lore credential path](../../veoveo-docs/LORE_DIRECT_OIDC_PLAN.md) qualifies.
That plan uses built-in local IdP mappings, native OpenShell refresh and native Lore
authorization. Generic runtime code remains provider-independent; external issuer
claim/refresh compatibility requires separate acceptance. No factory token endpoint
will be added to the Desktop adapter.

The separate `veoveo-service-lore` adapter now translates stable Desktop's published
`UrcAuthApi` login to this provider's OIDC flow, filters its repository catalog, and
keeps provider refresh credentials outside coding containers. The actual macOS
Desktop has passed browser login, catalog discovery and reconnect. Remote graph and
diff browsing were not completed and are now withdrawn requirements. See
[the current runtime](../README.md#lore-desktop-pending-retirement).

Automatic provider-expiry recovery was also incomplete: after Keycloak rejected an expired
refresh token, Desktop showed an authentication error and did not reopen sign-in.
The official CLI's browser login renewed the shared credential, and restarting
Desktop restored the four-repository catalog. Provider refresh and reload after
adapter restart passed on the OIDC portability revision. The tested manual recovery
procedure belonged to the former Desktop workflow. Seamless Desktop recovery no
longer blocks acceptance and must not justify retaining the adapter.

The adapter selects its provider through OIDC issuer/client/scopes configuration.
Only `identity/configure-lore-client` calls Keycloak administration APIs for local
development. The generic `desktop/configure-identity` deploys operator-supplied OIDC
configuration and credentials without Keycloak. The reference uses
`desktop/entra.example.json`; customers use `desktop/oidc.example.json`. These are
separate from the Gateway's `identity/entra.example.json` client registration.

Gateway's externally discoverable OAuth metadata still uses the existing internal
service issuer/token URLs; browser integrations use explicit HTTPS endpoints. Its
canonical human-facing discovery contract remains separate work.
