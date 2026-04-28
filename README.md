# mininet-graduação

Ambiente Docker para práticas de redes com Mininet.

Consulte também o [Guia Rápido Mininet](docs/GUIA_RAPIDO_MININET.md) e o [Erros comuns, reset e emergência](docs/ERROS_COMUNS_E_EMERGENCIA.md).

## Arquitetura

Visão completa da arquitetura do projeto:

- [docs/ARQUITETURA.md](docs/ARQUITETURA.md)

### Documentação em PDF (único arquivo)

Para gerar um único PDF com o README e os documentos referenciados (guia rápido, erros, arquitetura, métricas e laboratórios), use Docker e o script:

```bash
./scripts/build-docs-pdf.sh
```

O arquivo sai em `docs/mininet-graduacao-documentacao.pdf` (é necessário Docker; em Mac com Apple Silicon a imagem Pandoc roda em modo `linux/amd64`). Para outro caminho:

```bash
./scripts/build-docs-pdf.sh /caminho/dentro/do/repo/saida.pdf
```

## Coleta de métricas (automatizada)

A documentação da coleta de métricas está em:

- [metrics/README.md](metrics/README.md)

## Laboratórios

- [Lab 1 - TCP no Mininet](labs/lab1_tcp.md)
- [Lab 2 - Controle de Congestionamento](labs/lab2_congestionamento.md)
- [Lab 3 - Routing básico no Mininet](labs/lab3_routing.md)
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
docker run -it --rm --privileged --network host \
  -v "$(pwd):/workspace" -w /workspace \
  -e MININET_LAB_ROOT=/workspace \
  mininet-lab
```

Com isso, arquivos gerados em `metrics/runs/` dentro do container também aparecem no host.

## Preparação para criar topologias

As topologias dos laboratórios vêm de scripts Python na pasta `topologies/`.
Você pode:

- usar as topologias prontas (`topo_simples.py`, `topo_estrela.py`, `topo_lab4_2switches.py`);
- criar novas topologias para atividades da disciplina.

### Como criar uma nova topologia

1. Crie um arquivo em `topologies/`, por exemplo:

```bash
touch topologies/topo_meu_lab.py
```

2. Estruture o script com:
   - criação da rede (`Mininet`);
   - criação de hosts (`addHost`) e switches (`addSwitch`);
   - links (`addLink`);
   - `net.start()` e `net.stop()`;
   - opcionalmente `CLI(net)` para modo interativo.

3. Execute dentro do container:

```bash
python3 topologies/topo_meu_lab.py
```

### Regras recomendadas para os alunos

- Nomeie nós de forma consistente: hosts (`h1`, `h2`, ...), switches (`s1`, `s2`, ...), roteadores (`r1`, `r2`, ...).
- Defina IPs explícitos quando houver roteamento entre sub-redes.
- Habilite encaminhamento nos roteadores Linux:
  - `sysctl -w net.ipv4.ip_forward=1`
- Sempre valide a topologia com:
  - `pingall`
  - `iperf h1 h2` (ou pares equivalentes)
- Ao finalizar uma execução, limpe o estado antes de subir outra:
  - `mn -c`

### Quais topologias podem ser criadas

Exemplos úteis para a disciplina:

- linear (`h1 - s1 - s2 - h2`);
- estrela (vários hosts em um switch central);
- árvore (camadas de agregação/acesso);
- roteada com múltiplas sub-redes (`h1 - r1 - r2 - h2`);
- com emulação de link (`tc`) para atraso/perda/banda:
  - `delay`, `loss`, `bw`.

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
