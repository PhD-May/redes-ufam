#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

docker run -it --rm \
  --privileged \
  --network host \
  -v "${ROOT_DIR}:/workspace" \
  -w /workspace \
  -e MININET_LAB_ROOT=/workspace \
  mininet-lab
