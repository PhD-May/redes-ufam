# Lab 4 - Roteamento (opcional)

## Objetivos

- Configurar rotas manualmente.
- Criar topologia com 2 switches.

## Topologia sugerida

```text
h1 --- s1 --- r1 --- r2 --- s2 --- h2
```

`r1` e `r2` podem ser hosts Linux atuando como roteadores (`ip_forward=1`).

Script base disponível em:

- `topologies/topo_lab4_2switches.py`

## Passos propostos

1. Executar o script da topologia:

```bash
python3 topologies/topo_lab4_2switches.py
```

2. Verificar endereçamento IP das interfaces.
3. Verificar roteamento nos nós roteadores:

```bash
sysctl -w net.ipv4.ip_forward=1
```

4. Adicionar rotas estáticas manualmente:

```bash
ip route add <rede-destino> via <next-hop>
```

5. Validar conectividade ponta a ponta:
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
