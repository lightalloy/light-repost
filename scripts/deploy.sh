#!/usr/bin/env bash
set -euo pipefail

: "${DEPLOY_HOST:?Set DEPLOY_HOST}"
: "${DEPLOY_USER:?Set DEPLOY_USER}"
: "${DEPLOY_PATH:?Set DEPLOY_PATH (e.g. /opt/light-repost)}"

ssh "${DEPLOY_USER}@${DEPLOY_HOST}" bash -s <<EOF
set -euo pipefail
cd "${DEPLOY_PATH}"
docker compose pull
docker compose up -d
docker compose ps
EOF

echo "Deployed to ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}"
