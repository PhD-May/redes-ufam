#!/usr/bin/env python3
"""Topologia para o Lab 4: 2 switches + 2 roteadores + 2 hosts.

Topologia:
    h1 --- s1 --- r1 --- r2 --- s2 --- h2
"""

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch


def configure_nodes(h1, h2, r1, r2):
    """Configura IPs iniciais e habilita roteamento em r1/r2."""
    # Enderecamento:
    # h1-eth0 <-> r1-eth0: 10.0.1.0/24
    # r1-eth1 <-> r2-eth0: 10.0.12.0/24
    # r2-eth1 <-> h2-eth0: 10.0.2.0/24
    h1.cmd("ip addr add 10.0.1.10/24 dev h1-eth0")
    h2.cmd("ip addr add 10.0.2.10/24 dev h2-eth0")

    r1.cmd("ip addr add 10.0.1.1/24 dev r1-eth0")
    r1.cmd("ip addr add 10.0.12.1/24 dev r1-eth1")
    r2.cmd("ip addr add 10.0.12.2/24 dev r2-eth0")
    r2.cmd("ip addr add 10.0.2.1/24 dev r2-eth1")

    r1.cmd("sysctl -w net.ipv4.ip_forward=1")
    r2.cmd("sysctl -w net.ipv4.ip_forward=1")

    # Rotas default dos hosts.
    h1.cmd("ip route add default via 10.0.1.1")
    h2.cmd("ip route add default via 10.0.2.1")

    # Rotas entre roteadores para alcance fim-a-fim.
    r1.cmd("ip route add 10.0.2.0/24 via 10.0.12.2")
    r2.cmd("ip route add 10.0.1.0/24 via 10.0.12.1")


def run():
    net = Mininet(switch=OVSSwitch, build=False, autoSetMacs=True)

    h1 = net.addHost("h1")
    h2 = net.addHost("h2")
    r1 = net.addHost("r1")
    r2 = net.addHost("r2")

    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    net.addLink(h1, s1)  # h1-eth0
    net.addLink(s1, r1)  # r1-eth0
    net.addLink(r1, r2)  # r1-eth1 <-> r2-eth0
    net.addLink(r2, s2)  # r2-eth1
    net.addLink(s2, h2)  # h2-eth0

    net.build()
    net.start()

    configure_nodes(h1, h2, r1, r2)

    print("*** Teste rapido: ping h1 -> h2")
    print(h1.cmd("ping -c 3 10.0.2.10"))
    print("*** Entrando no CLI do Mininet")
    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
