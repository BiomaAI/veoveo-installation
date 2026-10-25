# Bioma Installation Design

Bioma's installation is the template's Linux path. It uses K3s for foundation
services and OpenShell's native Kubernetes driver for Hub/MCP, Computer and factory
workloads. The platform architecture lives in
[veoveo-docs](https://github.com/VeoveoAI/veoveo-docs/blob/main/ARCHITECTURE.md), the
installation design in the
[template's DESIGN](https://github.com/VeoveoAI/veoveo-template-installation/blob/main/DESIGN.md),
and qualification status in the
[checklist](https://github.com/VeoveoAI/veoveo-docs/blob/main/QUALIFICATION_CHECKLIST.md).
The ordinary [Kubernetes inputs](kubernetes/README.md) bootstrap PostgreSQL as a plain
StatefulSet, SeaweedFS, single-replica Lore, OpenShell gateway and the existing public
tunnel. K3s has an independent embedded datastore. Gateway and application PostgreSQL
roles/databases are distinct and share one PostgreSQL instance. This is a
single-node recovery target, not qualified multi-host HA.

Mac development and component/integration testing, with their Docker, Compose
and local Keycloak fixtures, stay in the template. Bioma uses Entra and has no
Mac or Compose launch path.

Lore owns source/revision semantics and enforces its unchanged native signed-token
contract. Entra authenticates humans; Hub's existing issuer and revisioned control
plane own explicit repository assignments/native token issuance. There is no
Desktop adapter, standalone signer, automatic creator/admin grant, custom Lore
permission layer or token worker. Factory renewal/injection belongs to native
OpenShell. Human native Lore grants remain in each private Computer.

Kubernetes/Helm owns foundation resources only. OpenShell owns dynamic workspace
namespaces, sandbox resources, policies, providers, templates, lifecycle and
persistent workspace PVCs. Existing APIs create/remove workloads; Helm values
must not inventory runtime sandboxes or force unrelated rollouts. Hub catalogs
are database-authoritative: initial files seed only an empty installation. Live
MCP request destinations, Computer defaults and explicit repository grants adopt
through the admitted control-plane path, preserving active state on rejection.
New defaults make a new Computer version, which new sandboxes start at; an existing
Computer keeps its recorded version until its owner restarts it.

Trusted server configuration lives in operator-populated, admitted, workspace-local
PVCs mounted read-only outside `/sandbox`. No caller Secret/ConfigMap/hostPath or
protected `/run` bypass is introduced. Computer `/sandbox` uses native automatic
per-sandbox persistence, never a shared explicit claim. Actual credentials,
private TLS/signing material and operator state are never tracked or included in
agent-controlled images. Only reviewed public CAs enter application build contexts.

Services/DNS provide private PostgreSQL, S3 and Lore addressing. Public origins
stay installation data. The tunnel preserves public signed S3 bytes and uses
verified TLS to native Services. Native controllers, readiness/restarts and
application retry/reconnect handle recovery; there is no custom startup DAG or
proxy. Dependency interruption and dynamic lifecycle behavior require deployed
qualification, separate from component tests and final exact MiMo acceptance.
