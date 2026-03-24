# Guia Rápido Mininet (1 página)

Referência rápida para uso no laboratório.

## Comandos essenciais

| Comando | O que faz |
|---|---|
| `mn` | Cria topologia padrão (`h1`, `h2`, `s1`). |
| `pingall` | Testa conectividade entre todos os hosts no CLI do Mininet. |
| `iperf` | Mede throughput TCP entre dois hosts no CLI do Mininet. |
| `net` | Mostra conexões entre hosts, switches e links. |
| `dump` | Mostra interfaces e configurações básicas dos nós. |

## Fluxo básico de uso

1. Iniciar o Mininet:

```bash
mn
```

2. No prompt `mininet>`, executar:

```bash
net
pingall
iperf h1 h2
dump
```

3. Sair corretamente:

```bash
exit
mn -c
```

## Dicas rápidas

- Se `pingall` falhar, rode `mn -c` e inicie novamente.
- Em container com usuário `root`, não use `sudo`.
- Para teste rápido sem entrar no CLI: `mn --test pingall`.
