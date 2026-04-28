# Arquitetura do Projeto

Este documento descreve a arquitetura do projeto `mininet-graduação` para facilitar entendimento e manutenção.

## Visão geral

O projeto usa Docker para entregar um ambiente de laboratório consistente com Mininet, Open vSwitch e ferramentas de medição de rede. A operação didática é guiada por documentação (`README`, `docs/`, `labs/`) e por scripts de apoio (`run.sh` e `collect_metrics.py`).

## Diagrama de componentes

```mermaid
flowchart LR
  usuario[AlunoProfessor]
  repositorio[mininet-graduacao]
  readme[README.md]
  docs[docs/]
  labs[labs/]
  topologias[topologies/]
  metricasDoc[metrics/README.md]

  dockerfile[Dockerfile]
  runsh[run.sh]
  entrypoint[docker-entrypoint.sh]
  coleta[scripts/collect_metrics.py]

  dockerEngine[DockerEngine]
  container[mininet-lab-container]
  ovs[OpenvSwitch]
  mininet[Mininet]
  ferramentas[ferramentas-rede]
  jsonOut[metrics/runs/run_timestamp.json]

  usuario --> readme
  readme --> docs
  readme --> labs
  readme --> topologias
  readme --> metricasDoc

  repositorio --> dockerfile
  repositorio --> runsh
  repositorio --> entrypoint
  repositorio --> coleta

  dockerfile --> dockerEngine
  runsh --> dockerEngine
  dockerEngine --> container
  entrypoint --> ovs
  container --> mininet
  mininet --> ovs
  mininet --> ferramentas
  coleta --> mininet
  coleta --> jsonOut
```

Versão estática (PNG):

![Diagrama de arquitetura](diagrama-arquitetura.png)

O diagrama fonte está em [`diagrama-arquitetura.mmd`](diagrama-arquitetura.mmd).

## Fluxo de execução

1. Build da imagem com `docker build -t mininet-lab .`.
2. Execução do ambiente com `./run.sh`.
3. `docker-entrypoint.sh` inicializa `ovsdb-server` e `ovs-vswitchd`.
4. Aluno executa experimentos com Mininet (`mn`, `pingall`, `iperf`).
5. Coleta automatizada opcional com `collect-metrics` ou `python3 scripts/collect_metrics.py`.
6. Resultados em JSON salvos em `metrics/runs/`.

## Blocos principais

- **Ambiente Docker**: definido em `Dockerfile`, padroniza dependências de rede.
- **Inicialização OVS**: `docker-entrypoint.sh` garante socket e processos do Open vSwitch.
- **Execução do laboratório**: `run.sh` simplifica parâmetros de execução do container.
- **Topologias e labs**: `topologies/` e `labs/` estruturam as práticas da disciplina.
- **Métricas automatizadas**: `scripts/collect_metrics.py` coleta latência/perda/vazão e exporta JSON.
