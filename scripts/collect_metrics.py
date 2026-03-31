#!/usr/bin/env python3
"""
Coleta automatizada de métricas no Mininet (ping + iperf3 em JSON).

Uso (dentro do container, como root):
  python3 scripts/collect_metrics.py
  python3 scripts/collect_metrics.py --bw 10 --delay 20ms --loss 2

Saída: metrics/runs/run_<timestamp>.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.topo import Topo


def _repo_root() -> Path:
    """Raiz do laboratório: pasta pai de `scripts/` ou diretório atual."""
    p = Path(__file__).resolve()
    if p.parent.name == "scripts":
        return p.parent.parent
    return Path.cwd()


def _default_output_dir() -> Path:
    env = os.environ.get("METRICS_OUTPUT_DIR")
    if env:
        return Path(env)
    root = os.environ.get("MININET_LAB_ROOT")
    if root:
        return Path(root) / "metrics" / "runs"
    return _repo_root() / "metrics" / "runs"


def _parse_ping_rtt(ping_output: str) -> dict:
    """Extrai estatísticas do `ping -c N -q` (Linux)."""
    out = {}
    m = re.search(
        r"min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)\s*ms",
        ping_output,
    )
    if m:
        out["rtt_min_ms"] = float(m.group(1))
        out["rtt_avg_ms"] = float(m.group(2))
        out["rtt_max_ms"] = float(m.group(3))
        out["rtt_mdev_ms"] = float(m.group(4))
    m2 = re.search(r"(\d+)% packet loss", ping_output)
    if m2:
        out["packet_loss_percent"] = float(m2.group(1))
    return out


def _iperf3_json(h1, h2, duration: int = 10) -> dict:
    """TCP throughput via iperf3 (-J)."""
    h1.cmd("killall -q iperf3 2>/dev/null || true")
    h1.cmd("iperf3 -s -D")
    time.sleep(1.0)
    raw = h2.cmd(f"iperf3 -c {h1.IP()} -t {duration} -J -4 2>/dev/null")
    h1.cmd("killall -q iperf3 2>/dev/null || true")
    start = raw.find("{")
    if start < 0:
        return {"error": "iperf3_json_parse_failed", "raw_tail": raw[-500:]}
    try:
        data = json.loads(raw[start:])
    except json.JSONDecodeError as e:
        return {"error": str(e), "raw_tail": raw[-500:]}
    end = data.get("end") or {}
    streams = end.get("streams") or []
    recv = end.get("sum_received") or {}
    sent = end.get("sum_sent") or {}
    bps = recv.get("bits_per_second") or sent.get("bits_per_second")
    out = {
        "protocol": "tcp",
        "duration_seconds": duration,
        "bits_per_second": bps,
        "mbits_per_second": round(float(bps) / 1e6, 3) if bps is not None else None,
    }
    if streams:
        out["retransmits"] = sum(
            s.get("sender", {}).get("retransmits", 0) for s in streams
        )
    return out


def _sysctl_tcp() -> dict:
    """Lê congestion control atual (melhor esforço)."""
    try:
        with open("/proc/sys/net/ipv4/tcp_congestion_control") as f:
            cc = f.read().strip()
        with open("/proc/sys/net/ipv4/tcp_available_congestion_control") as f:
            avail = f.read().strip().split()
        return {"tcp_congestion_control": cc, "tcp_available": avail}
    except OSError:
        return {}


def _single_switch_topo(link_kwargs: dict | None) -> Topo:
    """Mesma ideia do `mn` padrão: dois hosts e um switch."""

    class _T(Topo):
        def build(self):
            s1 = self.addSwitch("s1")
            h1 = self.addHost("h1")
            h2 = self.addHost("h2")
            if link_kwargs:
                self.addLink(h1, s1, **link_kwargs)
                self.addLink(h2, s1, **link_kwargs)
            else:
                self.addLink(h1, s1)
                self.addLink(h2, s1)

    return _T()


def collect(
    bw: float | None,
    delay: str | None,
    loss: float | None,
    ping_count: int,
    iperf_duration: int,
) -> dict:
    link_kwargs = {}
    if bw is not None:
        link_kwargs["bw"] = bw
    if delay is not None:
        link_kwargs["delay"] = delay
    if loss is not None:
        link_kwargs["loss"] = loss

    use_tc = bool(link_kwargs)
    topo = _single_switch_topo(link_kwargs if use_tc else {})
    # Run without external OpenFlow controller (same spirit as `mn` fallback).
    if use_tc:
        net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, controller=None)
    else:
        net = Mininet(topo=topo, switch=OVSSwitch, controller=None)

    net.start()
    time.sleep(0.5)
    h1 = net["h1"]
    h2 = net["h2"]
    try:
        ping_out = h1.cmd(f"ping -c {ping_count} -q {h2.IP()}")
        ping_metrics = _parse_ping_rtt(ping_out)
        ping_metrics["ping_count"] = ping_count

        loss_pct = net.pingAll()
        try:
            pingall_loss = float(loss_pct) if loss_pct is not None else None
        except (TypeError, ValueError):
            pingall_loss = None
        iperf_metrics = _iperf3_json(h1, h2, duration=iperf_duration)

        return {
            "schema": "mininet-lab-metrics/v1",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "link_emulation": link_kwargs if use_tc else None,
            "ping": ping_metrics,
            "pingall_loss_percent": pingall_loss,
            "iperf3": iperf_metrics,
            "sysctl_tcp": _sysctl_tcp(),
        }
    finally:
        net.stop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta métricas Mininet → JSON")
    parser.add_argument("--bw", type=float, default=None, help="Mbps (TCLink)")
    parser.add_argument("--delay", type=str, default=None, help='ex.: 20ms')
    parser.add_argument("--loss", type=float, default=None, help="percentual 0–100")
    parser.add_argument("--ping-count", type=int, default=10)
    parser.add_argument("--iperf-duration", type=int, default=10)
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Pasta de saída (default: METRICS_OUTPUT_DIR ou metrics/runs)",
    )
    args = parser.parse_args()

    if os.geteuid() != 0:
        print("Aviso: execute como root dentro do container para o Mininet.", file=sys.stderr)

    setLogLevel("warning")

    payload = collect(
        bw=args.bw,
        delay=args.delay,
        loss=args.loss,
        ping_count=args.ping_count,
        iperf_duration=args.iperf_duration,
    )

    out_dir = Path(args.output_dir) if args.output_dir else _default_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"run_{stamp}.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
