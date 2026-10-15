# syntax=docker/dockerfile:1.27@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e
ARG BASE
FROM ${BASE}
USER root
ARG TARGETARCH
# OpenCode v2's standalone binary, verified against the published npm integrity.
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* /var/log/apt /var/log/dpkg.log
RUN case "${TARGETARCH}" in \
      arm64) package=arm64; digest=EsCnvp5lMJNem0YoQJM9PkXY0KrkiugL55M9J2JlImQzKdQnZ4CKutrPAXOnsa889qHhY5tjRpAnD/ZYFzhkRA== ;; \
      amd64) package=x64; digest=pdG/T4uBxSC3hjUTOrTlx2pXlZl2VqABlb0AgDlZ8VO/q1pUUOYvooWmN5VeSi+EP8cKGVUsj0GUmMDeB2ympA== ;; \
      *) exit 1 ;; \
    esac \
    && curl --fail --silent --show-error --location "https://registry.npmjs.org/@opencode/cli-linux-${package}/-/cli-linux-${package}-2.0.29.tgz" -o /tmp/opencode.tgz \
    && test "$(openssl dgst -sha512 -binary /tmp/opencode.tgz | openssl base64 -A)" = "$digest" \
    && tar -xzf /tmp/opencode.tgz -C /tmp \
    && install -m 0755 /tmp/package/bin/opencode /usr/local/bin/opencode \
    && rm -rf /tmp/package /tmp/opencode.tgz
COPY --from=lore --chmod=0755 /usr/local/bin/lore /usr/local/bin/lore
COPY --from=ca --chmod=0644 ca.crt /usr/local/share/ca-certificates/veoveo-installation.crt
COPY --chmod=0644 opencode.json /etc/opencode/opencode.json
COPY --chmod=0644 instructions.txt /etc/opencode/instructions.txt
COPY --chmod=0644 loreignore /etc/opencode/loreignore
RUN (id sandbox >/dev/null 2>&1 || useradd --create-home --uid 1000 --shell /bin/bash sandbox) \
    && chmod 0755 /etc/opencode \
    && find / -xdev -type f -perm /6000 -exec chmod ug-s {} + \
    && update-ca-certificates >/dev/null \
    && mkdir -p /sandbox && chown sandbox:sandbox /sandbox
USER sandbox
WORKDIR /sandbox
CMD ["sleep", "infinity"]
