FROM node:24-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/apps/web/frontend

USER node

CMD ["sleep", "infinity"]
