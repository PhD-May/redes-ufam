# Lab 1 - TCP no Mininet

## Objetivos

- Medir throughput com `iperf`.
- Entender a diferença entre conectividade (`ping`) e vazão (`iperf`).
- Registrar um baseline TCP para os próximos laboratórios.

## Preparação

No host:

```bash
docker build -t mininet-lab .
./run.sh
```

Explicação:
- `docker build` cria a imagem com Mininet, Open vSwitch e ferramentas de medição.
- `./run.sh` sobe o container com privilégios de rede necessários para o laboratório.

No container:

```bash
mn --test pingall
mn --test iperf
```

Explicação:
- `mn --test pingall` valida conectividade básica entre hosts da topologia padrão.
- `mn --test iperf` verifica se o teste de vazão TCP está funcionando corretamente.

## Atividade 1 - Validar conectividade e serviços

Conceito:
- Antes de medir desempenho, é necessário validar se a rede básica está funcional.
- `pingall` confirma alcance entre hosts; `iperf` valida transferência TCP.

1. Rode `mn`.
2. No CLI do Mininet:
   - `pingall`
   - `iperf h1 h2`
3. Registre o resultado.

## Atividade 2 - Baseline TCP 

Conceito:
- Baseline é o cenário de referência sem atraso/perda artificiais.
- Esse valor será usado para comparar com os cenários degradados do Lab 2.

1. No CLI do Mininet, repita o teste 3 vezes:
   - `iperf h1 h2`
2. Calcule média aproximada da vazão obtida.
3. Registre o baseline na tabela.

## Atividade 3 - Conhecer o congestion control ativo

Conceito:
- O Linux usa um algoritmo de congestion control (ex.: `cubic`) para regular envio TCP.
- Neste lab, o objetivo é apenas identificar o algoritmo atual; comparação prática fica para o Lab 2.

No shell do container:

```bash
sysctl net.ipv4.tcp_available_congestion_control
sysctl net.ipv4.tcp_congestion_control
```

Explique no relatório qual algoritmo estava ativo durante o baseline.

## Roteiro de relatório (preencher)

Registre os resultados para comparação:

| Cenário | Comando de execução | RTT médio (ms) | Throughput (Mbit/s) | Perda (%) | Observações |
|---|---|---:|---:|---:|---|
| Baseline TCP | `mn` + `pingall` + `iperf h1 h2` |  |  |  |  |

## Quando usar o coletor de métricas

Fluxo recomendado para aprendizado:

1. Execute os comandos manualmente no Mininet para entender o que está acontecendo.
2. Ao finalizar o baseline, rode o coletor **uma vez** para registrar métricas em JSON.

Importante:
- Não é necessário rodar o coletor a cada comando (`pingall`, `iperf`, etc.).
- Neste Lab 1, use 1 execução do coletor para registrar o cenário baseline.

Exemplos:

```bash
# Cenário baseline do Lab 1
collect-metrics
```
