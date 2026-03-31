# Coleta de métricas

Os arquivos JSON são gerados automaticamente pelo script `scripts/collect_metrics.py` (ou pelo comando `collect-metrics` dentro da imagem Docker).

## Formato (`mininet-lab-metrics/v1`)

Cada execução produz um arquivo em `metrics/runs/` com nome `run_<timestamp>.json`, contendo:

- `timestamp_utc`: instante da coleta (UTC)
- `link_emulation`: parâmetros de emulação (`bw`, `delay`, `loss`) ou `null` se não houver `tc`
- `ping`: estatísticas do `ping` entre `h1` e `h2` (RTT e perda, quando disponíveis)
- `pingall_loss_percent`: perda reportada pelo `pingAll()` do Mininet
- `iperf3`: resultado TCP do `iperf3` em modo JSON (vazão em bit/s e Mbit/s)
- `sysctl_tcp`: algoritmo de congestionamento TCP atual (quando `/proc/sys` está acessível)

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

Ou defina só a pasta de saída:

```bash
docker run ... -e METRICS_OUTPUT_DIR=/workspace/metrics/runs mininet-lab collect-metrics
```
