# Gerar gráficos — Labs 1, 2 e 3

Guia com a sequência completa de comandos para coletar métricas, exportar CSV e gerar PNGs em `metrics/plots/`.

Documentação relacionada: [metrics/README.md](../metrics/README.md), [README.md](../README.md), [ERROS_COMUNS_E_EMERGENCIA.md](ERROS_COMUNS_E_EMERGENCIA.md).

---
mn
## Pré-requisitos (host)

```bash
docker build -t mininet-lab .
./run.sh
```

Dentro do container, os coletores `collect-metrics` e `collect-metrics-routing` já estão no `PATH`.

**Importante:** rode os coletores no shell do container (`root@...#`), **não** no prompt `mininet>`. Antes de cada coleta, saia do Mininet (`exit`) e limpe o estado:

```bash
exit    # se estiver no mininet>
mn -c
```

Os JSON ficam em `metrics/runs/` (visível no host porque `./run.sh` monta o volume do repositório).

---

## Lab 1 — TCP baseline

### Objetivo dos gráficos

Registrar o cenário de referência (sem `tc` de atraso/perda). Os PNGs do Lab 1 entram no mesmo CSV dos Labs 1–2 (`labs_1_2_runs.csv`).

### Coleta (container)

Após validar manualmente com `mn`, `pingall` e `iperf h1 h2`:

```bash
mn -c

# Baseline — uma execução por cenário
collect-metrics
```

Opcional — identificar o algoritmo TCP ativo (só para o relatório; o coletor já grava `tcp_congestion_control` no JSON):

```bash
sysctl net.ipv4.tcp_congestion_control
```

### Gráficos gerados (Labs 1–2)

Com apenas o baseline, os gráficos mostram um único cenário. A comparação visual fica mais rica após o Lab 2 (vários cenários e algoritmos).

---

## Lab 2 — Atraso, perda e algoritmos TCP

### Objetivo dos gráficos

Comparar **vazão**, **RTT** e **perda** entre cenários (base, delay, delay+loss) e entre algoritmos (`cubic`, `reno`, …).

### Coleta (container)

Uma execução do coletor por cenário (e por algoritmo, quando for comparar TCP):

```bash
mn -c

# Cenário base
collect-metrics

# Com atraso
collect-metrics --bw 10 --delay 30ms

# Atraso + perda (algoritmo padrão, em geral cubic)
collect-metrics --bw 10 --delay 30ms --loss 2

# Mesmo cenário com reno
sysctl -w net.ipv4.tcp_congestion_control=reno
collect-metrics --bw 10 --delay 30ms --loss 2

# Voltar ao padrão (recomendado)
sysctl -w net.ipv4.tcp_congestion_control=cubic
```

Para listar algoritmos disponíveis:

```bash
sysctl net.ipv4.tcp_available_congestion_control
```

### Gráficos gerados (Labs 1–2)

Após `./run.sh plots` (seção comum abaixo):

| Arquivo | Métrica |
|---------|---------|
| `metrics/plots/labs12_throughput_por_tcp_cc.png` | Vazão (Mbit/s) |
| `metrics/plots/labs12_rtt_por_tcp_cc.png` | RTT médio (ms) |
| `metrics/plots/labs12_perda_por_tcp_cc.png` | Perda ping (%) |
| `metrics/plots/labs12_painel_tcp_cc.png` | Painel com as três métricas |

---

## Lab 3 — Roteamento (h1–r1–r2–h2)

### Objetivo dos gráficos

Throughput e RTT **bidirecionais** por cenário de enlace no backbone (`r1`↔`r2`), com opção de degradar `core-delay` / `core-loss` / `core-bw`.

### Coleta (container)

```bash
mn -c

# Cenário base
collect-metrics-routing

# Backbone degradado (opcional)
collect-metrics-routing --core-bw 10 --core-delay 20ms --core-loss 2
```

Comparar algoritmos TCP no Lab 3 (opcional):

```bash
mn -c
sysctl -w net.ipv4.tcp_congestion_control=reno
collect-metrics-routing
sysctl -w net.ipv4.tcp_congestion_control=cubic
collect-metrics-routing
```

Cada coleta grava `metrics/runs/routing_run_<timestamp>.json`.

### Gráficos gerados (Lab 3)

| Arquivo | Conteúdo |
|---------|----------|
| `metrics/plots/lab3_throughput_direcoes.png` | Vazão h1→h2 e h2→h1 por cenário |
| `metrics/plots/lab3_rtt_direcoes.png` | RTT por direção |
| `metrics/plots/lab3_throughput_por_tcp_cc.png` | Vazão (se houver vários `tcp_congestion_control`) |
| `metrics/plots/lab3_rtt_por_tcp_cc.png` | RTT (se houver vários algoritmos) |

---

## Passos comuns — CSV e gráficos (host)

Execute no diretório do repositório, **fora** do container ou no host após sair do lab.

### 1. Agregar JSON em CSV

```bash
python3 scripts/json_runs_to_csv.py
```

Saída em `metrics/runs/`:

- `labs_1_2_runs.csv` — a partir de `run_*.json` (Labs 1 e 2)
- `lab3_runs.csv` — a partir de `routing_run_*.json` (Lab 3)

Opções:

```bash
python3 scripts/json_runs_to_csv.py --input-dir metrics/runs --output-dir metrics/runs
python3 scripts/json_runs_to_csv.py --combined   # também cria all_runs.csv
```

### 2. Gerar PNGs

```bash
./run.sh plots
```

O script:

1. Constrói a imagem `mininet-lab-plots` (Jupyter + pandas + matplotlib)
2. Reconverte JSON→CSV automaticamente (sempre que houver `run_*.json` ou `routing_run_*.json`)
3. Executa `notebooks/gerar_graficos.ipynb`
4. Salva figuras em `metrics/plots/`

### 3. (Opcional) Editar gráficos no Jupyter

```bash
./run.sh plots-lab
```

Abra http://localhost:8888 e o notebook `notebooks/gerar_graficos.ipynb`.

---

## Fluxo completo resumido

```bash
# === HOST ===
docker build -t mininet-lab .
./run.sh

# === CONTAINER — Lab 1 ===
mn -c && collect-metrics

# === CONTAINER — Lab 2 ===
mn -c && collect-metrics
mn -c && collect-metrics --bw 10 --delay 30ms
mn -c && collect-metrics --bw 10 --delay 30ms --loss 2
sysctl -w net.ipv4.tcp_congestion_control=reno
mn -c && collect-metrics --bw 10 --delay 30ms --loss 2
sysctl -w net.ipv4.tcp_congestion_control=cubic

# === CONTAINER — Lab 3 ===
mn -c && collect-metrics-routing
mn -c && collect-metrics-routing --core-bw 10 --core-delay 20ms --core-loss 2

# Sair do container (Ctrl+D ou exit)

# === HOST — gráficos ===
python3 scripts/json_runs_to_csv.py
./run.sh plots
ls metrics/plots/
```

---

## Coleta sem entrar no container interativo

Alternativa para rodar um cenário isolado no host:

```bash
# Lab 1/2
docker run --rm --privileged --network host \
  -v "$(pwd):/workspace" -w /workspace \
  -e MININET_LAB_ROOT=/workspace \
  mininet-lab collect-metrics --bw 10 --delay 30ms --loss 2

# Lab 3
docker run --rm --privileged --network host \
  -v "$(pwd):/workspace" -w /workspace \
  -e MININET_LAB_ROOT=/workspace \
  mininet-lab collect-metrics-routing --core-delay 20ms --core-loss 2
```

Depois, no host: `python3 scripts/json_runs_to_csv.py` e `./run.sh plots`.

---

## Métricas no CSV

| Métrica | Coluna principal (Labs 1–2) | Coluna principal (Lab 3) |
|---------|------------------------------|---------------------------|
| Vazão | `iperf_mbits_per_second` | `iperf_h1_to_h2_mbits_per_second`, `iperf_h2_to_h1_mbits_per_second` |
| Atraso (RTT) | `rtt_avg_ms` | `ping_h1_to_h2_rtt_avg_ms`, `ping_h2_to_h1_rtt_avg_ms` |
| Perda | `packet_loss_percent`, `pingall_loss_percent` | `ping_h1_to_h2_packet_loss_percent`, … |
| Algoritmo TCP | `tcp_congestion_control` | `tcp_congestion_control` |
| Cenário de emulação | `link_bw_mbps`, `link_delay`, `link_loss_percent` | `core_bw_mbps`, `core_delay`, `core_loss_percent` |

---

## Problemas comuns

| Sintoma | O que fazer |
|---------|-------------|
| Pasta `metrics/plots/` vazia | Conferir se há JSON em `metrics/runs/`; rodar `json_runs_to_csv.py` e `./run.sh plots` de novo |
| Gráfico sem comparação de algoritmos | Coletar pelo menos duas vezes com `sysctl -w net.ipv4.tcp_congestion_control=...` diferentes |
| Poucos cenários no eixo X | Rodar mais `collect-metrics` / `collect-metrics-routing` (um JSON por cenário) |
| Erro de rede no container | Ver [ERROS_COMUNS_E_EMERGENCIA.md](ERROS_COMUNS_E_EMERGENCIA.md) |
