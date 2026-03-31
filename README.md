# mininet-graduação

Ambiente Docker para práticas de redes com Mininet.

Consulte também o [Guia Rápido Mininet](docs/GUIA_RAPIDO_MININET.md) e o [Erros comuns, reset e emergência](docs/ERROS_COMUNS_E_EMERGENCIA.md).

## Coleta de métricas (automatizada)

A documentação da coleta de métricas está em:

- [metrics/README.md](metrics/README.md)

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
mn -c
```

Se você estiver usando Mininet instalado diretamente no host Linux, use:

```bash
sudo mn -c
```
