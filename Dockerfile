FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      mininet \
      openvswitch-switch \
      iperf \
      iperf3 \
      tcpdump \
      iproute2 \
      iputils-ping \
      python3 \
      python3-pip \
      net-tools \
      vim \
      ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

COPY scripts/ /opt/mininet-lab/scripts/
RUN chmod +x /opt/mininet-lab/scripts/collect_metrics.py /opt/mininet-lab/scripts/collect_metrics_routing.py && \
    ln -sf /opt/mininet-lab/scripts/collect_metrics.py /usr/local/bin/collect-metrics && \
    ln -sf /opt/mininet-lab/scripts/collect_metrics_routing.py /usr/local/bin/collect-metrics-routing

ENV MININET_LAB_ROOT=/opt/mininet-lab

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/bin/bash"]
