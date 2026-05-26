#!/usr/bin/env python3
"""
Coleta automatizada de métricas para topologia roteada (Lab 3).

Topologia: h1 --- r1 --- r2 --- h2

Uso:
  python3 scripts/collect_metrics_routing.py
  python3 scripts/collect_metrics_routing.py --core-delay 20ms

Saída: metrics/runs/routing_run_<timestamp>.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo


def _repo_root() -> Path:
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


#
# Observação sobre IPs em Lab 3:
# depois de `ip addr add ...` nos nós, o método Node.IP() do Mininet pode
# continuar retornando o IP padrão original alocado pelo Mininet.
# Para evitar métricas erradas, usamos explicitamente os IPs configurados.
#
H1_IP = "10.0.1.10"
H2_IP = "10.0.2.10"


def _iperf3_json(src, dst, src_ip: str, duration: int = 10) -> dict:
    src.cmd("killall -q iperf3 2>/dev/null || true")
    src.cmd("iperf3 -s -D")
    time.sleep(1.0)
    raw = dst.cmd(f"iperf3 -c {src_ip} -t {duration} -J -4 2>/dev/null")
    src.cmd("killall -q iperf3 2>/dev/null || true")
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


class RoutingTopo(Topo):
    """Lab 3: links ponto a ponto entre hosts e roteadores."""

    def __init__(self, core_link_kwargs: dict | None = None):
        self.core_link_kwargs = core_link_kwargs or {}
        super().__init__()

    def build(self):
        h1 = self.addHost("h1")
        r1 = self.addHost("r1")
        r2 = self.addHost("r2")
        h2 = self.addHost("h2")

        self.addLink(h1, r1)
        if self.core_link_kwargs:
            self.addLink(r1, r2, **self.core_link_kwargs)
        else:
            self.addLink(r1, r2)
        self.addLink(r2, h2)


def _sysctl_tcp() -> dict:
    try:
        with open("/proc/sys/net/ipv4/tcp_congestion_control") as f:
            cc = f.read().strip()
        with open("/proc/sys/net/ipv4/tcp_available_congestion_control") as f:
            avail = f.read().strip().split()
        return {"tcp_congestion_control": cc, "tcp_available": avail}
    except OSError:
        return {}


def _flush_mininet_default_addrs(net: Mininet) -> None:
    """Remove IPs /8 do Mininet (10.0.0.0/8) que quebram roteamento entre sub-redes."""
    for host, intfs in (
        (net["h1"], ("h1-eth0",)),
        (net["h2"], ("h2-eth0",)),
        (net["r1"], ("r1-eth0", "r1-eth1")),
        (net["r2"], ("r2-eth0", "r2-eth1")),
    ):
        for intf in intfs:
            host.cmd(f"ip addr flush dev {intf}")


def _configure_routing_nodes(net: Mininet) -> None:
    h1, h2, r1, r2 = net["h1"], net["h2"], net["r1"], net["r2"]

    _flush_mininet_default_addrs(net)

    h1.cmd("ip addr add 10.0.1.10/24 dev h1-eth0")
    h2.cmd("ip addr add 10.0.2.10/24 dev h2-eth0")
    r1.cmd("ip addr add 10.0.1.1/24 dev r1-eth0")
    r1.cmd("ip addr add 10.0.12.1/24 dev r1-eth1")
    r2.cmd("ip addr add 10.0.12.2/24 dev r2-eth0")
    r2.cmd("ip addr add 10.0.2.1/24 dev r2-eth1")

    r1.cmd("sysctl -w net.ipv4.ip_forward=1")
    r2.cmd("sysctl -w net.ipv4.ip_forward=1")
    h1.cmd("ip route add default via 10.0.1.1")
    h2.cmd("ip route add default via 10.0.2.1")
    r1.cmd("ip route add 10.0.2.0/24 via 10.0.12.2")
    r2.cmd("ip route add 10.0.1.0/24 via 10.0.12.1")


def collect(
    core_bw,
    core_delay,
    core_loss,
    ping_count: int,
    iperf_duration: int,
) -> dict:
    core_link_kwargs = {}
    if core_bw is not None:
        core_link_kwargs["bw"] = core_bw
    if core_delay is not None:
        core_link_kwargs["delay"] = core_delay
    if core_loss is not None:
        core_link_kwargs["loss"] = core_loss

    topo = RoutingTopo(core_link_kwargs=core_link_kwargs)
    # Topologia ponto a ponto (sem switches), como topologies/topo_lab3_routing.py
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.start()
    time.sleep(0.5)
    _configure_routing_nodes(net)
    time.sleep(0.5)

    h1, h2, r1, r2 = net["h1"], net["h2"], net["r1"], net["r2"]
    try:
        ping_h1_h2_raw = h1.cmd(f"ping -c {ping_count} -q {H2_IP}")
        ping_h2_h1_raw = h2.cmd(f"ping -c {ping_count} -q {H1_IP}")
        pingall_loss = net.pingAll()
        iperf_h1_h2 = _iperf3_json(h1, h2, src_ip=H1_IP, duration=iperf_duration)
        iperf_h2_h1 = _iperf3_json(h2, h1, src_ip=H2_IP, duration=iperf_duration)

        return {
            "schema": "mininet-routing-metrics/v1",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "topology": "h1-r1-r2-h2",
            "core_link_emulation": core_link_kwargs if core_link_kwargs else None,
            "ping": {
                "h1_to_h2": {"ping_count": ping_count, **_parse_ping_rtt(ping_h1_h2_raw)},
                "h2_to_h1": {"ping_count": ping_count, **_parse_ping_rtt(ping_h2_h1_raw)},
            },
            "pingall_loss_percent": float(pingall_loss) if pingall_loss is not None else None,
            "iperf3": {"h1_to_h2": iperf_h1_h2, "h2_to_h1": iperf_h2_h1},
            "routes": {"r1": r1.cmd("ip route").strip(), "r2": r2.cmd("ip route").strip()},
            "sysctl_tcp": _sysctl_tcp(),
        }
    finally:
        net.stop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta métricas para topologia roteada (Lab 3)")
    parser.add_argument("--core-bw", type=float, default=None, help="Mbps no link r1<->r2")
    parser.add_argument("--core-delay", type=str, default=None, help="ex.: 20ms no link r1<->r2")
    parser.add_argument("--core-loss", type=float, default=None, help="percentual no link r1<->r2")
    parser.add_argument("--ping-count", type=int, default=10)
    parser.add_argument("--iperf-duration", type=int, default=10)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    setLogLevel("warning")
    payload = collect(
        core_bw=args.core_bw,
        core_delay=args.core_delay,
        core_loss=args.core_loss,
        ping_count=args.ping_count,
        iperf_duration=args.iperf_duration,
    )

    out_dir = Path(args.output_dir) if args.output_dir else _default_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"routing_run_{stamp}.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
