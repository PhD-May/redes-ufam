#!/usr/bin/env python3
"""Topologia simples: 2 hosts conectados por 1 switch."""

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch


def run():
    net = Mininet(switch=OVSSwitch)
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")
    s1 = net.addSwitch("s1")

    net.addLink(h1, s1)
    net.addLink(h2, s1)

    net.start()
    print("*** Teste rapido: pingall")
    net.pingAll()
    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
