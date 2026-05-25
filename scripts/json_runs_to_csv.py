#!/usr/bin/env python3
"""
Agrega JSONs de metrics/runs/ em CSV para gráficos.

Entrada (gerados pelos coletores):
  run_<timestamp>.json           -> collect-metrics (Labs 1/2)
  routing_run_<timestamp>.json   -> collect-metrics-routing (Lab 3)

Saída (padrão, na mesma pasta de entrada):
  labs_1_2_runs.csv — run_*.json (Labs 1 e 2, collect-metrics)
  lab3_runs.csv     — routing_run_*.json (Lab 3, collect-metrics-routing)
  all_runs.csv      — opcional, com --combined (não mistura colunas dos dois labs)

Uso:
  python3 scripts/json_runs_to_csv.py
  python3 scripts/json_runs_to_csv.py --input-dir metrics/runs --output-dir metrics/runs
  python3 scripts/json_runs_to_csv.py --combined
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def _repo_root() -> Path:
    p = Path(__file__).resolve()
    if p.parent.name == "scripts":
        return p.parent.parent
    return Path.cwd()


def _default_input_dir() -> Path:
    root = _repo_root()
    env_root = __import__("os").environ.get("MININET_LAB_ROOT")
    if env_root:
        return Path(env_root) / "metrics" / "runs"
    return root / "metrics" / "runs"


def _link_fields(emulation: dict | None, prefix: str) -> dict:
    if not emulation:
        return {f"{prefix}_bw_mbps": None, f"{prefix}_delay": None, f"{prefix}_loss_percent": None}
    return {
        f"{prefix}_bw_mbps": emulation.get("bw"),
        f"{prefix}_delay": emulation.get("delay"),
        f"{prefix}_loss_percent": emulation.get("loss"),
    }


def _col(prefix: str, name: str) -> str:
    return f"{prefix}_{name}" if prefix else name


def _ping_fields(ping: dict | None, prefix: str) -> dict:
    if not ping:
        ping = {}
    return {
        _col(prefix, "ping_count"): ping.get("ping_count"),
        _col(prefix, "rtt_min_ms"): ping.get("rtt_min_ms"),
        _col(prefix, "rtt_avg_ms"): ping.get("rtt_avg_ms"),
        _col(prefix, "rtt_max_ms"): ping.get("rtt_max_ms"),
        _col(prefix, "rtt_mdev_ms"): ping.get("rtt_mdev_ms"),
        _col(prefix, "packet_loss_percent"): ping.get("packet_loss_percent"),
    }


def _iperf_fields(iperf: dict | None, prefix: str) -> dict:
    if not iperf:
        iperf = {}
    # Labs 1/2: prefix vazio -> iperf_duration_s, iperf_mbits_per_second, ...
    p = prefix or "iperf"
    return {
        _col(p, "duration_s"): iperf.get("duration_seconds"),
        _col(p, "mbits_per_second"): iperf.get("mbits_per_second"),
        _col(p, "bits_per_second"): iperf.get("bits_per_second"),
        _col(p, "retransmits"): iperf.get("retransmits"),
        _col(p, "error"): iperf.get("error"),
    }


def flatten_lab_run(path: Path, data: dict) -> dict:
    sysctl = data.get("sysctl_tcp") or {}
    avail = sysctl.get("tcp_available")
    row = {
        "source_file": path.name,
        "lab": "1-2",
        "kind": "lab",
        "schema": data.get("schema"),
        "timestamp_utc": data.get("timestamp_utc"),
        "pingall_loss_percent": data.get("pingall_loss_percent"),
        "tcp_congestion_control": sysctl.get("tcp_congestion_control"),
        "tcp_available": ",".join(avail) if isinstance(avail, list) else avail,
    }
    row.update(_link_fields(data.get("link_emulation"), "link"))
    row.update(_ping_fields(data.get("ping"), ""))
    row.update(_iperf_fields(data.get("iperf3"), ""))
    return row


def flatten_routing_run(path: Path, data: dict) -> dict:
    sysctl = data.get("sysctl_tcp") or {}
    avail = sysctl.get("tcp_available")
    row = {
        "source_file": path.name,
        "lab": "3",
        "kind": "routing",
        "schema": data.get("schema"),
        "timestamp_utc": data.get("timestamp_utc"),
        "topology": data.get("topology"),
        "pingall_loss_percent": data.get("pingall_loss_percent"),
        "tcp_congestion_control": sysctl.get("tcp_congestion_control"),
        "tcp_available": ",".join(avail) if isinstance(avail, list) else avail,
    }
    row.update(_link_fields(data.get("core_link_emulation"), "core"))
    ping = data.get("ping") or {}
    row.update(_ping_fields(ping.get("h1_to_h2"), "ping_h1_to_h2"))
    row.update(_ping_fields(ping.get("h2_to_h1"), "ping_h2_to_h1"))
    iperf = data.get("iperf3") or {}
    row.update(_iperf_fields(iperf.get("h1_to_h2"), "iperf_h1_to_h2"))
    row.update(_iperf_fields(iperf.get("h2_to_h1"), "iperf_h2_to_h1"))
    return row


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _combined_row(lab: dict | None, routing: dict | None) -> dict:
    """Uma linha unificada com colunas comuns para gráficos simples."""
    base = lab or routing or {}
    row = {
        "source_file": base.get("source_file"),
        "lab": base.get("lab"),
        "kind": base.get("kind"),
        "schema": base.get("schema"),
        "timestamp_utc": base.get("timestamp_utc"),
        "topology": base.get("topology"),
        "pingall_loss_percent": base.get("pingall_loss_percent"),
        "tcp_congestion_control": base.get("tcp_congestion_control"),
        # emulação: link_* (lab) ou core_* (routing)
        "emul_bw_mbps": base.get("link_bw_mbps") or base.get("core_bw_mbps"),
        "emul_delay": base.get("link_delay") or base.get("core_delay"),
        "emul_loss_percent": base.get("link_loss_percent") or base.get("core_loss_percent"),
        # ping/iperf “principal” h1->h2
        "rtt_avg_ms": base.get("rtt_avg_ms") or base.get("ping_h1_to_h2_rtt_avg_ms"),
        "packet_loss_percent": base.get("packet_loss_percent")
        or base.get("ping_h1_to_h2_packet_loss_percent"),
        "iperf_mbits_per_second": base.get("iperf_mbits_per_second")
        or base.get("iperf_h1_to_h2_mbits_per_second"),
    }
    return row


def collect_rows(input_dir: Path) -> tuple[list[dict], list[dict]]:
    lab_rows: list[dict] = []
    routing_rows: list[dict] = []

    for path in sorted(input_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Ignorando {path.name}: {e}")
            continue

        schema = data.get("schema", "")
        if path.name.startswith("routing_run_") or schema == "mininet-routing-metrics/v1":
            routing_rows.append(flatten_routing_run(path, data))
        elif path.name.startswith("run_") or schema == "mininet-lab-metrics/v1":
            lab_rows.append(flatten_lab_run(path, data))
        else:
            print(f"Ignorando {path.name}: schema desconhecido ({schema!r})")

    lab_rows.sort(key=lambda r: r.get("timestamp_utc") or "")
    routing_rows.sort(key=lambda r: r.get("timestamp_utc") or "")
    return lab_rows, routing_rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Agrega run_*.json e routing_run_*.json em CSV para gráficos"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default=None,
        help="Pasta com JSONs (default: metrics/runs no repo ou MININET_LAB_ROOT)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Pasta de saída CSV (default: mesma que --input-dir)",
    )
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Gera também all_runs.csv com colunas resumidas (lab + routing)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir) if args.input_dir else _default_input_dir()
    output_dir = Path(args.output_dir) if args.output_dir else input_dir

    if not input_dir.is_dir():
        print(f"Pasta não encontrada: {input_dir}")
        return 1

    lab_rows, routing_rows = collect_rows(input_dir)

    labs_12_csv = output_dir / "labs_1_2_runs.csv"
    lab3_csv = output_dir / "lab3_runs.csv"

    _write_csv(labs_12_csv, lab_rows)
    _write_csv(lab3_csv, routing_rows)

    written = []
    if lab_rows:
        written.append(str(labs_12_csv))
    if routing_rows:
        written.append(str(lab3_csv))

    if args.combined:
        combined = [_combined_row(r, None) for r in lab_rows]
        combined += [_combined_row(None, r) for r in routing_rows]
        combined.sort(key=lambda r: r.get("timestamp_utc") or "")
        all_csv = output_dir / "all_runs.csv"
        _write_csv(all_csv, combined)
        if combined:
            written.append(str(all_csv))

    if not written:
        print(f"Nenhum JSON encontrado em {input_dir}")
        return 0

    for p in written:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
