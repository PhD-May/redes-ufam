# Lab 1 - TCP no Mininet

## Objetivos

- Medir throughput com `iperf`.
- Introduzir `tc` para adicionar atraso na rede.
- Observar efeito da troca de algoritmo de congestion control.

## Preparação

No host:

```bash
docker build -t mininet-lab .
./run.sh
```

No container:

```bash
mn --test pingall
mn --test iperf
```

## Atividade 1 - Throughput baseline

1. Rode `mn`.
2. No CLI do Mininet:
   - `iperf h1 h2`
3. Registre o resultado.

## Atividade 2 - Delay com tc

1. Saia do Mininet e rode:
   - `mn --link tc,bw=10,delay=20ms`
2. No CLI:
   - `pingall`
   - `iperf h1 h2`
3. Compare com o baseline.

## Atividade 3 - Congestion control

No shell do container:

```bash
sysctl net.ipv4.tcp_available_congestion_control
sysctl -w net.ipv4.tcp_congestion_control=cubic
```

Repita testes de `iperf` e compare.
