#!/usr/bin/env python3
"""Topologia estrela: N hosts conectados a 1 switch central."""

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch


def run(host_count=4):
    net = Mininet(switch=OVSSwitch)
    switch = net.addSwitch("s1")

    for i in range(1, host_count + 1):
        host = net.addHost(f"h{i}")
        net.addLink(host, switch)

    net.start()
    print("*** Teste rapido: pingall")
    net.pingAll()
    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()
