#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE_LAB="${MININET_LAB_IMAGE:-mininet-lab}"
IMAGE_PLOTS="${MININET_PLOTS_IMAGE:-mininet-lab-plots}"

usage() {
  cat <<'EOF'
Uso: ./run.sh [comando]

Comandos:
  lab        Ambiente Mininet interativo (padrão)
  plots      Gera gráficos (Docker + notebook) em metrics/plots/
  plots-lab  Jupyter Lab interativo na porta 8888 (gráficos/notebook)

Exemplos:
  ./run.sh
  ./run.sh lab
  ./run.sh plots
  ./run.sh plots-lab
EOF
}

run_lab() {
  docker run -it --rm \
    --privileged \
    --network host \
    -v "${ROOT_DIR}:/workspace" \
    -w /workspace \
    -e MININET_LAB_ROOT=/workspace \
    "${IMAGE_LAB}"
}

build_plots_image() {
  docker build -f "${ROOT_DIR}/Dockerfile.plots" -t "${IMAGE_PLOTS}" "${ROOT_DIR}"
}

ensure_csv() {
  if [[ ! -f "${ROOT_DIR}/metrics/runs/labs_1_2_runs.csv" ]] \
    && compgen -G "${ROOT_DIR}/metrics/runs/run_"*.json >/dev/null 2>&1; then
    echo "Convertendo JSON -> CSV..."
    docker run --rm \
      -v "${ROOT_DIR}:/workspace" \
      -w /workspace \
      "${IMAGE_LAB}" \
      python3 scripts/json_runs_to_csv.py || python3 "${ROOT_DIR}/scripts/json_runs_to_csv.py"
  fi
}

run_plots() {
  build_plots_image
  ensure_csv
  mkdir -p "${ROOT_DIR}/metrics/plots"
  docker run --rm \
    -v "${ROOT_DIR}:/workspace" \
    -w /workspace \
    "${IMAGE_PLOTS}"
  echo "Gráficos em: ${ROOT_DIR}/metrics/plots/"
}

run_plots_lab() {
  build_plots_image
  ensure_csv
  docker run -it --rm \
    -p 8888:8888 \
    -v "${ROOT_DIR}:/workspace" \
    -w /workspace \
    "${IMAGE_PLOTS}" \
    jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root \
    --NotebookApp.token='' --NotebookApp.password=''
}

CMD="${1:-lab}"
shift || true

case "${CMD}" in
  lab|"")
    run_lab "$@"
    ;;
  plots|graficos|graphs)
    run_plots "$@"
    ;;
  plots-lab|jupyter)
    run_plots_lab "$@"
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Comando desconhecido: ${CMD}" >&2
    usage >&2
    exit 1
    ;;
esac
