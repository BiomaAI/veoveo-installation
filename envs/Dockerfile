# syntax=docker/dockerfile:1.27@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e
# The installation's layer over an environment image (D40, D41). It adds the setgid
# Lore client, which reads the environment's token from /run/lore/token and sends it
# only to the installation's Lore server, and the installation's CA. The environment
# runs without no-new-privileges so the client can read its token, so the layer removes
# every other setuid and setgid program. Build contexts: `lore` is the vv-lore image,
# `ca` holds the installation CA's public certificate.
ARG BASE
FROM ${BASE}
USER root
# Packages a base image lacks, such as Git for the Lore admin container.
ARG PACKAGES=""
RUN if [ -n "${PACKAGES}" ]; then \
        apt-get update && apt-get install -y --no-install-recommends ${PACKAGES} \
        && rm -rf /var/lib/apt/lists/* /var/log/apt /var/log/dpkg.log; \
    fi
COPY --from=lore /usr/local/bin/lore /usr/local/bin/lore
COPY --from=ca --chmod=0644 ca.crt /usr/local/share/ca-certificates/veoveo-installation.crt
RUN (id sandbox >/dev/null 2>&1 || useradd --create-home --uid 1000 --shell /bin/bash sandbox) \
    && groupadd --system --gid 990 lore-cred \
    && find / -xdev -type f -perm /6000 -exec chmod ug-s {} + \
    && update-ca-certificates >/dev/null \
    && chown root:lore-cred /usr/local/bin/lore && chmod 2755 /usr/local/bin/lore \
    && mkdir -p /etc/lore /run/lore /sandbox \
    && printf 'remote = "lores://vv-lore.internal:41337"\n' > /etc/lore/sandbox.toml \
    && chmod 0644 /etc/lore/sandbox.toml \
    && chown root:lore-cred /run/lore && chmod 0750 /run/lore \
    && chown sandbox:sandbox /sandbox
USER sandbox
WORKDIR /sandbox
