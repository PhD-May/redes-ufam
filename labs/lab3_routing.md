# Lab 3 - Routing básico no Mininet

## Objetivos

- Montar topologia com mais de uma sub-rede.
- Configurar e verificar roteamento IP nos nós intermediários.
- Configurar rotas estáticas.
- Validar conectividade fim-a-fim com `ping` e `traceroute`.

## Preparação

No host:

```bash
docker build -t mininet-lab .
./run.sh
```

Explicação:
- `docker build` garante mesmo ambiente para toda a turma (inclui `traceroute`).
- `./run.sh` sobe o container com o repositório montado em `/workspace`.

## Topologia do Lab 3

```text
h1 --- r1 --- r2 --- h2
```

Plano de endereçamento (referência):

| Nó | Interface | IP / rede |
|---|---|---|
| `h1` | `h1-eth0` | `10.0.1.10/24` |
| `r1` | `r1-eth0` | `10.0.1.1/24` |
| `r1` | `r1-eth1` | `10.0.12.1/24` |
| `r2` | `r2-eth0` | `10.0.12.2/24` |
| `r2` | `r2-eth1` | `10.0.2.1/24` |
| `h2` | `h2-eth0` | `10.0.2.10/24` |

Conceito:
- `r1` e `r2` são hosts Linux com `ip_forward=1` atuando como roteadores.
- Links ponto a ponto entre nós são válidos no Mininet; não é obrigatório usar switch no meio do caminho.

Script pronto:

- `topologies/topo_lab3_routing.py`

## Atividade 1 - Subir a topologia

Conceito:
- A rede é dividida em sub-redes (`10.0.1.0/24`, `10.0.12.0/24`, `10.0.2.0/24`).
- Sem roteamento e rotas estáticas, hosts de sub-redes diferentes não se alcançam.

No shell do container:

```bash
python3 topologies/topo_lab3_routing.py
```

O script sobe a topologia, aplica IPs/rotas e abre o prompt `mininet>`.

## Atividade 2 - Verificar endereçamento IP

Conceito:
- Cada interface precisa de IP na sub-rede correta.
- Erros de máscara ou interface errada impedem o encaminhamento.

No prompt `mininet>`:

```bash
h1 ip addr show dev h1-eth0
r1 ip addr
r2 ip addr
h2 ip addr show dev h2-eth0
```

Confirme os IPs da tabela de referência.

## Atividade 3 - Habilitar e conferir roteamento nos intermediários

Conceito:
- Com `net.ipv4.ip_forward=1`, o kernel encaminha pacotes entre interfaces.
- Sem isso, `r1` e `r2` não roteiam tráfego de outras sub-redes.

No prompt `mininet>`:

```bash
r1 sysctl net.ipv4.ip_forward
r2 sysctl net.ipv4.ip_forward
```

Resultado esperado: `net.ipv4.ip_forward = 1` em ambos.

Se precisar habilitar manualmente:

```bash
r1 sysctl -w net.ipv4.ip_forward=1
r2 sysctl -w net.ipv4.ip_forward=1
```

## Atividade 4 - Conferir rotas estáticas

Conceito:
- Hosts usam rota default para o roteador da sub-rede local.
- Roteadores precisam de rotas para redes remotas (`10.0.2.0/24` e `10.0.1.0/24`).

No prompt `mininet>`:

```bash
h1 ip route
h2 ip route
r1 ip route
r2 ip route
```

Rotas esperadas (resumo):

- `h1`: default via `10.0.1.1`
- `h2`: default via `10.0.2.1`
- `r1`: `10.0.2.0/24 via 10.0.12.2`
- `r2`: `10.0.1.0/24 via 10.0.12.1`

## Atividade 5 - Validar conectividade fim-a-fim

Conceito:
- `ping` confirma alcance básico entre sub-redes.
- `traceroute` mostra os saltos (`r1`, `r2`) no caminho.

No prompt `mininet>`:

```bash
h1 ping -c 5 10.0.2.10
h2 ping -c 5 10.0.1.10
h1 traceroute 10.0.2.10
```

Registre RTT, perda e saltos observados.

## Atividade 6 - Medir throughput TCP

Conceito:
- Após o roteamento funcionar, a vazão TCP depende dos enlaces e da pilha do kernel.
- Serve para comparar cenário base com degradação no enlace `r1<->r2` (atividade opcional).

No prompt `mininet>`:

```bash
iperf h1 h2
```

Anote throughput e estabilidade.

## Atividade 7 (opcional) - Degradar o enlace entre roteadores

Conceito:
- Atraso/perda no backbone (`r1<->r2`) afeta RTT e throughput fim-a-fim.
- O coletor automatizado aceita `--core-delay`, `--core-loss` e `--core-bw` nesse enlace.

Saia do Mininet (`exit`) e limpe o estado:

```bash
mn -c
```

Depois use o coletor (ver seção abaixo) com parâmetros, por exemplo:

```bash
collect-metrics-routing --core-bw 10 --core-delay 20ms --core-loss 2
```

## Entregáveis

- Diagrama ou descrição da topologia.
- Tabela de rotas de `h1`, `h2`, `r1` e `r2`.
- Evidências de `ping` e `traceroute` fim-a-fim.
- Throughput TCP (`iperf`) no cenário base.

## Roteiro de relatório (preencher)

| Cenário | Comando principal | RTT médio (ms) | Throughput (Mbit/s) | Perda (%) | Saltos no traceroute | Observações |
|---|---|---:|---:|---:|---|---|
| Base | `python3 topologies/topo_lab3_routing.py` + `ping`/`traceroute` |  |  |  |  |  |
| Base | `iperf h1 h2` |  |  |  |  |  |
| Backbone degradado (opcional) | `collect-metrics-routing --core-delay 20ms --core-loss 2` |  |  |  |  |  |

| Etapa | Comando principal | Resultado esperado | Resultado obtido | Observações |
|---|---|---|---|---|
| Topologia criada | `python3 topologies/topo_lab3_routing.py` | Nós e links sobem sem erro |  |  |
| IPs configurados | `ip addr` | Interfaces com IP correto |  |  |
| Roteamento habilitado | `sysctl net.ipv4.ip_forward` | Valor `1` em `r1` e `r2` |  |  |
| Rotas estáticas | `ip route` | Rotas para redes remotas presentes |  |  |
| Conectividade final | `ping` / `traceroute` | Comunicação fim-a-fim funcional |  |  |

## Quando usar o coletor de métricas (roteamento)

Fluxo recomendado para aprendizado:

1. Execute o laboratório manualmente no Mininet para entender cada comando.
2. Ao final de cada cenário (base e, se fizer, backbone degradado), rode o coletor **uma vez** para gerar JSON estruturado.

Importante:
- Execute `collect-metrics-routing` no shell do container (`root@...#`), não no prompt `mininet>`.
- Antes do coletor, saia do Mininet e rode `mn -c`.

Exemplos:

```bash
# Cenário base (topologia h1-r1-r2-h2)
collect-metrics-routing

# Emular condições no enlace r1<->r2
collect-metrics-routing --core-bw 10 --core-delay 20ms --core-loss 2
```

O coletor grava `metrics/runs/routing_run_<timestamp>.json` (visível no host quando `./run.sh` monta o volume).
