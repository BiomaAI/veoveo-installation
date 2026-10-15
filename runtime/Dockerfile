# syntax=docker/dockerfile:1.27@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e
# Trusted runtime tooling. Source is an approved snapshot; Lore and coding agents
# live in the separate autonomy profile. No client token or privileged helper here.
ARG BASE
FROM ${BASE}
USER root
COPY --from=ca --chmod=0644 ca.crt /usr/local/share/ca-certificates/veoveo-installation.crt
RUN (id sandbox >/dev/null 2>&1 || useradd --create-home --uid 1000 --shell /bin/bash sandbox) \
    && find / -xdev -type f -perm /6000 -exec chmod ug-s {} + \
    && update-ca-certificates >/dev/null \
    && mkdir -p /sandbox && chown sandbox:sandbox /sandbox
USER sandbox
WORKDIR /sandbox
CMD ["sleep", "infinity"]
