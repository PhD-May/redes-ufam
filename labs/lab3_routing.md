# Lab 3 - Routing básico no Mininet

## Objetivos

- Montar topologia com mais de uma sub-rede.
- Configurar rotas estáticas.
- Validar conectividade entre redes.

## Preparação

No host:

```bash
docker build -t mininet-lab .
./run.sh
```

## Sugestão de topologia

- `h1 -- r1 -- r2 -- h2`

Onde `r1` e `r2` são hosts Linux com `ip_forward=1`.

## Atividade 1 - Montagem da topologia

Conceito:
- Esta etapa separa a rede em mais de uma sub-rede para mostrar quando roteamento é necessário.
- Sem roteamento, hosts de sub-redes diferentes não se alcançam corretamente.

1. Criar topologia customizada em Python.
2. Atribuir IPs nas interfaces.

## Atividade 2 - Habilitar roteamento nos nós intermediários

Conceito:
- `r1` e `r2` atuam como roteadores Linux.
- Com `ip_forward=1`, o kernel passa a encaminhar pacotes entre interfaces.

1. Habilitar roteamento:
   - `sysctl -w net.ipv4.ip_forward=1`
2. Verificar se o valor foi aplicado:
   - `sysctl net.ipv4.ip_forward`

## Atividade 3 - Configurar rotas estáticas

Conceito:
- Rotas estáticas definem o próximo salto para redes remotas.
- Sem essas rotas, os pacotes chegam ao roteador, mas podem não encontrar caminho até o destino.

1. Adicionar rotas:
   - `ip route add ...`
2. Conferir tabela de rotas em cada nó:
   - `ip route`

## Atividade 4 - Validar conectividade fim-a-fim

Conceito:
- O objetivo é comprovar que os pacotes atravessam roteadores e chegam à outra sub-rede.
- `ping` valida alcance básico e `traceroute` mostra o caminho percorrido.

1. Validar:
   - `ping`
   - `traceroute` (se instalado)

## Entregáveis

- Script da topologia.
- Tabela de rotas de cada nó.
- Evidências de conectividade fim-a-fim.

## Roteiro de relatório (preencher)

| Etapa | Comando principal | Resultado esperado | Resultado obtido | Observações |
|---|---|---|---|---|
| Topologia criada | `python3 <topologia>.py` | Nós e links sobem sem erro |  |  |
| IPs configurados | `ip addr` | Interfaces com IP correto |  |  |
| Roteamento habilitado | `sysctl net.ipv4.ip_forward` | Valor `1` em `r1` e `r2` |  |  |
| Rotas estáticas | `ip route` | Rotas para redes remotas presentes |  |  |
| Conectividade final | `ping` / `traceroute` | Comunicação fim-a-fim funcional |  |  |

## Quando usar o coletor de métricas (roteamento)

Fluxo recomendado:

1. Execute o laboratório manualmente para entender cada comando.
2. Ao final do cenário, rode o coletor de roteamento **uma vez** para gerar JSON estruturado.

```bash
collect-metrics-routing
```

Opcional (emular condições no enlace `r1<->r2`):

```bash
collect-metrics-routing --core-bw 10 --core-delay 20ms --core-loss 2
```
