#!/usr/bin/env bash
set -euo pipefail

docker run -it --rm \
  --privileged \
  --network host \
  mininet-lab
