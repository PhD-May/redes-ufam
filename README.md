# mininet-graduação

Ambiente Docker para práticas de redes com Mininet.

Consulte também o [Guia Rápido Mininet](docs/GUIA_RAPIDO_MININET.md) e o [Erros comuns, reset e emergência](docs/ERROS_COMUNS_E_EMERGENCIA.md).

## Coleta de métricas (automatizada)

O script `scripts/collect_metrics.py` sobe uma topologia simples (`h1`–`s1`–`h2`), mede **ping**, **pingAll** e **iperf3** (JSON) e grava um arquivo em `metrics/runs/run_<timestamp>.json`.

**Dentro do container** (repositório montado ou cópia em `/opt/mininet-lab` na imagem):

```bash
python3 scripts/collect_metrics.py
# ou, na imagem Docker:
collect-metrics
```

**Com emulação de link** (ex.: Lab 3 — atraso e perda):

```bash
python3 scripts/collect_metrics.py --bw 10 --delay 30ms --loss 2
```

Detalhes do formato e como **persistir JSON no host** com `docker run -v`: veja [metrics/README.md](metrics/README.md).

## Laboratórios

- [Lab 1 - TCP no Mininet](labs/lab1_tcp.md)
- [Lab 2 - Routing básico no Mininet](labs/lab2_routing.md)
- [Lab 3 - Controle de Congestionamento](labs/lab3_controle_congestionamento.md)
- [Lab 4 - Roteamento (opcional)](labs/lab4_routing_opcional.md)

Topologia pronta para o Lab 4:

- `topologies/topo_lab4_2switches.py`

## Pré-requisitos

- Docker instalado no computador
- Terminal (Linux/macOS/WSL)
- Git (opcional, para clonar o repositório)

> Recomendado: Linux para melhor compatibilidade de rede.

## Instalação do Docker

Escolha sua plataforma:

- Ubuntu/Linux: [Docker Engine](https://docs.docker.com/engine/install/)
- Windows/macOS: [Docker Desktop](https://docs.docker.com/get-started/get-docker/)

Depois de instalar, valide:

```bash
docker --version
docker run --rm hello-world
```

## Como rodar o projeto

1. Build da imagem:

```bash
docker build -t mininet-lab .
```

2. Subir o laboratório:

```bash
./run.sh
```

`run.sh` executa:

```bash
docker run -it --rm --privileged --network host mininet-lab
```

## Comandos básicos Mininet

Dentro do container:

```bash
mn                    # inicia topologia padrão
mn --test pingall     # teste de conectividade
mn --test iperf       # teste de throughput TCP
mn --link tc,bw=10,delay=10ms   # emulação com atraso
```

No prompt do Mininet (`mininet>`), comandos úteis:

```bash
nodes
net
h1 ping -c 3 h2
iperf h1 h2
```

## Como sair corretamente

1. No prompt `mininet>`, digite:

```bash
exit
```

2. No shell do container, limpe o estado do Mininet:

```bash
sudo mn -c
```

Se `sudo` não existir no container (execução como root), use:

```bash
mn -c
```
