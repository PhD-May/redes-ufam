#!/usr/bin/env bash
set -euo pipefail

OVS_RUN_DIR="/var/run/openvswitch"
OVS_DB_DIR="/etc/openvswitch"
OVS_DB_SOCK="${OVS_RUN_DIR}/db.sock"
OVS_DB_FILE="${OVS_DB_DIR}/conf.db"
OVS_SCHEMA="/usr/share/openvswitch/vswitch.ovsschema"

start_ovs() {
  mkdir -p "${OVS_RUN_DIR}" "${OVS_DB_DIR}"

  if [ ! -f "${OVS_DB_FILE}" ]; then
    ovsdb-tool create "${OVS_DB_FILE}" "${OVS_SCHEMA}"
  fi

  if [ ! -S "${OVS_DB_SOCK}" ]; then
    ovsdb-server \
      --remote=punix:${OVS_DB_SOCK} \
      --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
      --pidfile --detach "${OVS_DB_FILE}"
  fi

  ovs-vsctl --no-wait init

  if ! pgrep -x ovs-vswitchd >/dev/null 2>&1; then
    ovs-vswitchd unix:${OVS_DB_SOCK} --pidfile --detach
  fi
}

start_ovs

exec "$@"
