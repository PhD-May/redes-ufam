# Coleta de métricas

Os arquivos JSON são gerados automaticamente pelos scripts:

- `scripts/collect_metrics.py` (`collect-metrics`): topologia simples `h1-s1-h2` (Labs 1 e 2).
- `scripts/collect_metrics_routing.py` (`collect-metrics-routing`): topologia roteada `h1-r1-r2-h2` (Lab 3).

## Formato (`mininet-lab-metrics/v1`)

Cada execução produz um arquivo em `metrics/runs/` com nome `run_<timestamp>.json`, contendo:

- `timestamp_utc`: instante da coleta (UTC)
- `link_emulation`: parâmetros de emulação (`bw`, `delay`, `loss`) ou `null` se não houver `tc`
- `ping`: estatísticas do `ping` entre `h1` e `h2` (RTT e perda, quando disponíveis)
- `pingall_loss_percent`: perda reportada pelo `pingAll()` do Mininet
- `iperf3`: resultado TCP do `iperf3` em modo JSON (vazão em bit/s e Mbit/s)
- `sysctl_tcp`: algoritmo de congestionamento TCP atual (quando `/proc/sys` está acessível)

## Formato roteado (`mininet-routing-metrics/v1`)

Cada execução produz um arquivo em `metrics/runs/` com nome `routing_run_<timestamp>.json`, contendo:

- `topology`: sempre `h1-r1-r2-h2`
- `core_link_emulation`: parâmetros no enlace entre roteadores (`core-bw`, `core-delay`, `core-loss`)
- `ping`: métricas bidirecionais (`h1->h2` e `h2->h1`)
- `pingall_loss_percent`: perda reportada por `pingAll()`
- `iperf3`: throughput bidirecional (`h1->h2` e `h2->h1`)
- `routes`: tabelas de rota de `r1` e `r2`
- `sysctl_tcp`: algoritmo TCP ativo na coleta (mesmo formato dos Labs 1–2)

## Persistir resultados no host

Por padrão, dentro do container os arquivos ficam em `/opt/mininet-lab/metrics/runs`. Para gravar na pasta do repositório no seu computador:

```bash
docker run -it --rm --privileged --network host \
  -v "$(pwd):/workspace" \
  -w /workspace \
  -e MININET_LAB_ROOT=/workspace \
  mininet-lab \
  python3 scripts/collect_metrics.py
```

Para o coletor de roteamento:

```bash
docker run -it --rm --privileged --network host \
  -v "$(pwd):/workspace" \
  -w /workspace \
  -e MININET_LAB_ROOT=/workspace \
  mininet-lab \
  python3 scripts/collect_metrics_routing.py
```

Ou defina só a pasta de saída:

```bash
docker run ... -e METRICS_OUTPUT_DIR=/workspace/metrics/runs mininet-lab collect-metrics
```

Exemplo do coletor roteado com emulação no enlace `r1<->r2`:

```bash
collect-metrics-routing
collect-metrics-routing --core-bw 10 --core-delay 20ms --core-loss 2
```

Sim, **é o coletor que gera o JSON** (não o comando `mn` interativo). O arquivo é escrito automaticamente em `metrics/runs/`.

## Exportar para CSV (gráficos)

Depois de rodar os coletores, agregue os JSON em CSV:

```bash
python3 scripts/json_runs_to_csv.py
```

Gera (na pasta `metrics/runs/`):

- `labs_1_2_runs.csv` — a partir de `run_*.json` (Labs 1/2)
- `lab3_runs.csv` — a partir de `routing_run_*.json` (Lab 3, arquivo separado)

Opções:

```bash
python3 scripts/json_runs_to_csv.py --input-dir metrics/runs --output-dir metrics/runs
python3 scripts/json_runs_to_csv.py --combined   # também cria all_runs.csv (resumo)
```

Os CSV podem ser abertos no Excel, LibreOffice, pandas ou ferramentas de plotagem.

## Gráficos

Com CSVs prontos, gere figuras em `metrics/plots/`:

```bash
./run.sh plots
```

`./run.sh plots` tenta converter JSON→CSV automaticamente se existir `run_*.json` e ainda não houver `labs_1_2_runs.csv`.

Gráficos principais (Labs 1–2): comparação de throughput, RTT e perda por cenário e `tcp_congestion_control` (`cubic`, `reno`, …). Lab 3: throughput e RTT bidirecionais por cenário (e por `tcp_congestion_control` se houver coletas com algoritmos diferentes).

Para comparar algoritmos TCP, rode coletas com `sysctl -w net.ipv4.tcp_congestion_control=reno` (ou `cubic`) antes de cada `collect-metrics`.
