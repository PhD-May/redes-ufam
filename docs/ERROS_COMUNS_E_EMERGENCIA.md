# Erros comuns e comandos de emergência

Guia rápido para quando algo “trava” ou o laboratório não sobe como esperado.

## Erros comuns

| Sintoma | Causa provável | O que fazer |
|--------|----------------|-------------|
| `ovs-vsctl: ... db.sock: No such file or directory` | Open vSwitch não está rodando (ou container antigo sem entrypoint). | No **container deste projeto**, saia e suba de novo com `./run.sh` (o script de entrada inicia o OVS). Em instalação **nativa** no Linux, reinicie o serviço: `sudo systemctl restart openvswitch-switch`. |
| `bash: sudo: command not found` | O container roda como **root**; `sudo` não vem instalado. | Use os comandos **sem** `sudo` (por exemplo `mn -c` em vez de `sudo mn -c`). |
| `mn` falha após fechar o terminal sem `exit` | Estado antigo de namespaces, interfaces ou bridges. | Rode `mn -c` (ou `sudo mn -c` no host Linux). |
| `pingall` falha ou comportamento estranho | Topologia anterior ainda parcialmente ativa. | `exit` no CLI do Mininet, depois `mn -c` e tente de novo. |
| Permissão negada ao usar Docker | Daemon do Docker não acessível ou usuário fora do grupo `docker`. | No Linux: `sudo usermod -aG docker $USER` e novo login; ou use `sudo docker ...`. |
| `collect-metrics` não encontrado ou JSON não aparece no PC | Coletor rodado fora do container, sem volume, ou no prompt `mininet>`. | Use `./run.sh`; rode coletores no shell `root@...#` após `mn -c`; confira `metrics/runs/` no host. |
| Gráficos vazios ou “sem dados” | CSV ausente ou só um algoritmo TCP nas coletas. | `python3 scripts/json_runs_to_csv.py`; para comparar `cubic` vs `reno`, duas coletas com `sysctl -w` entre elas. |

## Como resetar o Mininet

1. Saia do prompt `mininet>` com `exit`.
2. Limpe o estado do Mininet:

**Dentro do container (usuário root, sem `sudo`):**

```bash
mn -c
```

**No Linux instalado nativamente (com sudo):**

```bash
sudo mn -c
```

Isso remove interfaces virtuais, namespaces e bridges criados pelo Mininet naquela máquina/container.

## Como limpar o Docker

Use quando quiser liberar espaço ou garantir que não há containers antigos da imagem `mininet-lab`.

- Listar containers parados:

```bash
docker ps -a
```

- Remover containers parados:

```bash
docker container prune
```

- Remover imagem deste laboratório (após isso, faça `docker build` de novo):

```bash
docker rmi mininet-lab
```

- Limpeza mais ampla (cuidado: afeta **tudo** que não estiver em uso):

```bash
docker system prune -a
```

Confirme com atenção quando o Docker pedir; `prune -a` remove imagens não utilizadas em geral.

## Preparar comandos de emergência

Guarde estes comandos em um bloco de notas ou alias no shell para usar na ordem quando nada mais funcionar.

### Dentro do container deste projeto

```bash
exit          # se ainda estiver no mininet>
mn -c
```

Depois **feche** o container (`exit` no bash) e suba de novo:

```bash
./run.sh
```

### No Linux com Mininet/Open vSwitch instalados no host

**Reset completo** (limpa Mininet e reinicia o Open vSwitch):

```bash
sudo mn -c
sudo systemctl restart openvswitch-switch
```

> No **container** deste repositório normalmente **não** existe `systemctl`; o OVS é iniciado pelo `docker-entrypoint.sh` ao abrir o container — nesse caso, prefira sair do container e executar `./run.sh` novamente.

### Se o problema for só Docker

```bash
docker ps -a
docker stop <id_ou_nome>   # se algum container mininet-lab estiver preso
docker container prune     # opcional
./run.sh                   # novo shell limpo
```

## Resumo

| Onde | Reset Mininet | Reiniciar OVS |
|------|---------------|---------------|
| Container `mininet-lab` | `mn -c` | Sair e rodar `./run.sh` de novo |
| Ubuntu/Linux (nativo) | `sudo mn -c` | `sudo systemctl restart openvswitch-switch` |
