# Lab 4 - Roteamento (opcional)

## Objetivos

- Configurar rotas manualmente.
- Criar topologia com 2 switches.

## Preparação

No host:

```bash
docker build -t mininet-lab .
./run.sh
```

Explicação:
- `docker build` cria o ambiente de laboratório com dependências de rede.
- `./run.sh` sobe o container com permissões adequadas para o Mininet.

## Topologia sugerida

```text
h1 --- s1 --- r1 --- r2 --- s2 --- h2
```

`r1` e `r2` podem ser hosts Linux atuando como roteadores (`ip_forward=1`).

Script base disponível em:

- `topologies/topo_lab4_2switches.py`

## Atividade 1 - Subir a topologia com 2 switches

Conceito:
- Esta topologia separa domínios de camada 2 (`s1` e `s2`) e força comunicação via roteadores.
- É um cenário mais próximo de redes reais com múltiplos segmentos.

1. Executar o script da topologia:

```bash
python3 topologies/topo_lab4_2switches.py
```

2. Verificar endereçamento IP das interfaces.

## Atividade 2 - Confirmar função de roteador em r1 e r2

Conceito:
- `ip_forward=1` transforma os nós em roteadores Linux.
- Sem esse passo, os nós não encaminham tráfego entre interfaces.

1. Verificar roteamento nos nós roteadores:

```bash
sysctl -w net.ipv4.ip_forward=1
```

2. Confirmar:
   - `sysctl net.ipv4.ip_forward`

## Atividade 3 - Configurar rotas estáticas manualmente

Conceito:
- Rotas estáticas definem o próximo salto para atingir redes fora do segmento local.
- A qualidade dessas rotas determina se haverá conectividade ponta a ponta.

1. Adicionar rotas estáticas manualmente:

```bash
ip route add <rede-destino> via <next-hop>
```

2. Conferir tabelas de roteamento:
   - `ip route`

## Atividade 4 - Validar conectividade ponta a ponta

Conceito:
- Os testes finais comprovam se a topologia e o plano de rotas estão corretos.
- `traceroute` ajuda a verificar se o caminho esperado está sendo usado.

1. Validar conectividade ponta a ponta:
   - `ping`
   - `iperf`
   - `traceroute` (se disponível)

## Comandos úteis no CLI do Mininet

```bash
nodes
net
r1 ip route
r2 ip route
h1 ping -c 3 h2
iperf h1 h2
```

## Entregáveis

- Código da topologia com 2 switches.
- Tabela de rotas de todos os nós.
- Evidências dos testes de conectividade.

## Roteiro de relatório (preencher)

| Etapa | Comando principal | Resultado esperado | Resultado obtido | Observações |
|---|---|---|---|---|
| Topologia com 2 switches | `python3 topologies/topo_lab4_2switches.py` | Nós e links ativos |  |  |
| Roteadores habilitados | `sysctl net.ipv4.ip_forward` | Valor `1` em `r1` e `r2` |  |  |
| Rotas estáticas | `ip route` | Rotas para redes remotas presentes |  |  |
| Ping ponta a ponta | `h1 ping -c 3 h2` | Resposta com perda baixa/zero |  |  |
| Vazão ponta a ponta | `iperf h1 h2` | Throughput consistente com cenário |  |  |

## Quando usar o coletor de métricas (roteamento)

Após validar a topologia manualmente, gere um JSON para análise posterior:

```bash
collect-metrics-routing
```

Para testar impacto de atraso/perda no enlace entre roteadores:

```bash
collect-metrics-routing --core-bw 10 --core-delay 20ms --core-loss 2
```
