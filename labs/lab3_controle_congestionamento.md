# Lab 3 - Controle de Congestionamento

## Objetivos

- Introduzir atraso (`delay`) na rede.
- Introduzir perda (`loss`) na rede.
- Avaliar o impacto no desempenho TCP.

## Preparação

No host:

```bash
docker build -t mininet-lab .
./run.sh
```

## Atividade 1 - Cenário base

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

## Entregáveis

- Tabela com resultados: base vs delay vs delay+loss.
- Curta análise do impacto de delay e loss no TCP.
