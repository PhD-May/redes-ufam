# Lab 2 - Routing básico no Mininet

## Objetivos

- Montar topologia com mais de uma sub-rede.
- Configurar rotas estáticas.
- Validar conectividade entre redes.

## Sugestão de topologia

- `h1 -- r1 -- r2 -- h2`

Onde `r1` e `r2` são hosts Linux com `ip_forward=1`.

## Passos gerais

1. Criar topologia customizada em Python.
2. Atribuir IPs nas interfaces.
3. Habilitar roteamento:
   - `sysctl -w net.ipv4.ip_forward=1`
4. Adicionar rotas:
   - `ip route add ...`
5. Validar:
   - `ping`
   - `traceroute` (se instalado)

## Entregáveis

- Script da topologia.
- Tabela de rotas de cada nó.
- Evidências de conectividade fim-a-fim.
