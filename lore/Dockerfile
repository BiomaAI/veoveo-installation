# syntax=docker/dockerfile:1.27@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e
# Lore's server and client from VeoveoAI/lore: Lore v0.10.1 with the client patches of
# D41, pinned to one commit. Every host builds from source, because Lore's arm64 release
# binaries carry a Neoverse tuning that Apple Silicon does not run.
FROM rust:1.99.0-trixie@sha256:6ff07edce8775d0f64be7aba9197229407301bddf2054d62c27b541a6238a181 AS build
RUN apt-get update \
    && apt-get install -y --no-install-recommends protobuf-compiler libprotobuf-dev \
    && rm -rf /var/lib/apt/lists/* /var/log/apt /var/log/dpkg.log
ADD https://github.com/VeoveoAI/lore.git#36808ddf85dc98034e704f9de59939d4a3e24fa4 /build
WORKDIR /build
RUN --mount=type=cache,target=/usr/local/cargo/registry,sharing=locked \
    --mount=type=cache,target=/usr/local/cargo/git,sharing=locked \
    --mount=type=cache,target=/build/target,sharing=locked \
    cargo build --release --locked --bin lore --bin loreserver \
    && install -D -m 0755 target/release/lore target/release/loreserver -t /out

FROM debian:trixie-slim@sha256:a29215f6a35e51e22adffa17f89e9d2ef06214e64a2bad10d765c46aea49f11f
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* /var/log/apt /var/log/dpkg.log
COPY --from=build /out/lore /out/loreserver /usr/local/bin/
# The server's shipped defaults, then the installation's settings in local.toml.
COPY --from=build /build/lore-server/config/default.toml /etc/lore/config/default.toml
ENV LORE_CONFIG_PATH=/etc/lore/config
EXPOSE 41337/tcp 41337/udp
ENTRYPOINT ["loreserver"]
