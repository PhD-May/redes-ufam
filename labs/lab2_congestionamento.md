# Lab 2 - Controle de Congestionamento

## Objetivos

- Introduzir atraso (`delay`) na rede.
- Introduzir perda (`loss`) na rede.
- Avaliar o impacto no desempenho TCP.
- Comparar comportamento entre algoritmos de congestion control.

## Preparação

No host:

```bash
docker build -t mininet-lab .
./run.sh
```

Explicação:
- `docker build` garante mesmo ambiente para toda a turma.
- `./run.sh` sobe o container já preparado para experimentos de rede.

## Atividade 1 - Cenário base

Conceito:
- Mede o comportamento TCP sem degradação artificial.
- Esse cenário serve de referência para comparar os demais.

No container:

```bash
mn
```

No prompt `mininet>`:

```bash
pingall
iperf h1 h2
```

Registre latência e throughput do cenário sem degradação.

## Atividade 2 - Introduzir atraso (delay)

Conceito:
- O atraso aumenta o RTT e pode reduzir a eficiência do TCP.
- Simula enlaces de longa distância (WAN).

No shell do container:

```bash
mn -c
mn --link tc,bw=10,delay=30ms
```

No prompt `mininet>`:

```bash
pingall
iperf h1 h2
```

Compare os resultados com o cenário base.

## Atividade 3 - Introduzir perda (loss)

Conceito:
- Perda de pacotes gera retransmissões e ativa mecanismos de controle de congestionamento.
- Em geral, perda causa queda de vazão e maior variabilidade do throughput.

No shell do container:

```bash
mn -c
mn --link tc,bw=10,delay=30ms,loss=2
```

No prompt `mininet>`:

```bash
pingall
iperf h1 h2
```

Observe como a perda afeta vazão e estabilidade da conexão.

## Atividade 4 - Comparar algoritmo TCP (cubic vs reno)

Conceito:
- Algoritmos de congestion control respondem de forma diferente a delay e perda.
- Comparar `cubic` e `reno` ajuda a entender adaptação de janela e retransmissões.

No shell do container:

```bash
sysctl net.ipv4.tcp_available_congestion_control
sysctl -w net.ipv4.tcp_congestion_control=reno
```

Repita o cenário com `delay+loss` e registre resultados.
Depois, retorne para `cubic`:

```bash
sysctl -w net.ipv4.tcp_congestion_control=cubic
```

## Entregáveis

- Tabela com resultados: base vs delay vs delay+loss.
- Curta análise do impacto de delay, loss e algoritmo TCP no desempenho.

## Roteiro de relatório (preencher)

| Cenário | Algoritmo TCP | Comando de execução | RTT médio (ms) | Throughput (Mbit/s) | Perda (%) | Observações |
|---|---|---|---:|---:|---:|---|
| Base | `cubic` | `mn` + `iperf h1 h2` |  |  |  |  |
| Delay | `cubic` | `mn --link tc,bw=10,delay=30ms` |  |  |  |  |
| Delay + loss | `cubic` | `mn --link tc,bw=10,delay=30ms,loss=2` |  |  |  |  |
| Delay + loss | `reno` | `mn --link tc,bw=10,delay=30ms,loss=2` |  |  |  |  |

## Quando usar o coletor de métricas

Fluxo recomendado para aprendizado:

1. Execute os comandos manualmente no Mininet para entender o que está acontecendo.
2. Ao finalizar cada cenário (base, delay, delay+loss e teste com `reno`), rode o coletor **uma vez** para registrar métricas em JSON.

Importante:
- Não é necessário rodar o coletor a cada comando (`pingall`, `iperf`, etc.).
- Use 1 execução do coletor por cenário para gerar dados comparáveis.
- Execute `collect-metrics` no shell do container (`root@...#`), não no prompt `mininet>`.

Exemplos:

```bash
# Cenário base
collect-metrics

# Cenário com atraso
collect-metrics --bw 10 --delay 30ms

# Cenário com atraso + perda
collect-metrics --bw 10 --delay 30ms --loss 2

# Mesmo cenário com algoritmo reno
sysctl -w net.ipv4.tcp_congestion_control=reno
collect-metrics --bw 10 --delay 30ms --loss 2
sysctl -w net.ipv4.tcp_congestion_control=cubic
```
