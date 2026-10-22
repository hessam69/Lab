FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends nftables iproute2 iputils-ping curl python3 procps && rm -rf /var/lib/apt/lists/*
