#!/usr/bin/env python3
"""Topologia para o Lab 3: roteamento com links ponto a ponto (sem switches).

Topologia:
    h1 --- r1 --- r2 --- h2

Cada enlace é um segmento L3; r1 e r2 atuam como roteadores Linux (ip_forward=1).
Não é obrigatório usar switch entre roteadores — links diretos host-host são válidos no Mininet.
"""

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet


def configure_nodes(h1, h2, r1, r2):
    """Configura IPs e rotas estáticas do Lab 3."""
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


def run():
    net = Mininet(controller=None)

    h1 = net.addHost("h1")
    r1 = net.addHost("r1")
    r2 = net.addHost("r2")
    h2 = net.addHost("h2")

    net.addLink(h1, r1)  # h1-eth0 <-> r1-eth0
    net.addLink(r1, r2)  # r1-eth1 <-> r2-eth0
    net.addLink(r2, h2)  # r2-eth1 <-> h2-eth0

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
