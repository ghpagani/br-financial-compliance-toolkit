# Handoff entre agentes

Canal real de comunicação: **Orca orchestration** (`orca orchestration send|reply|check`). O terminal do Codex (`Implementador`) é uma caixa de correio de terminal **viva**: a entrega não é durável se o terminal fechar. Por isso este arquivo e o backlog são a fonte da verdade; a mensagem só aponta para eles.

## Papéis

| Agente | Branch | Faz | Não faz |
|---|---|---|---|
| Claude (líder/revisor) | `ghpagani/br-financial-compliance-toolkit` (integração) | auditoria, backlog, revisão de diff, testes, docs, integração local | push, merge em `main`, release |
| Codex (Implementador) | `ghpagani/Implementador` | implementa tarefas T-xxx em commits focados | editar fora do escopo da tarefa, desabilitar sandbox, push |

Os dois worktrees compartilham o mesmo repositório Git local, então o Claude lê os commits do Codex diretamente (`git log ghpagani/Implementador`), sem remoto.

## Protocolo de uma tarefa

1. Claude envia `send` com: ID da tarefa e o caminho `docs/DEVELOPMENT-BACKLOG.md#T-xxx`, **SHA de base**.
2. Codex: `git reset --hard <SHA de base>` **somente se a branch estiver limpa e sem trabalho próprio** (ou `git rebase`); implementa; roda `python -m unittest discover -s tests -v`; faz **um commit** `T-xxx: <resumo>`.
3. Codex responde com: SHA, lista de arquivos, saída resumida dos testes (contagem e resultado), desvios do escopo, dúvidas.
4. Claude revisa `git diff <base>..<sha>`, roda testes na própria árvore, confere critérios de aceitação, registra em `VALIDATION-REPORT.md`.
5. Aceita → Claude integra (`git merge --no-ff`; ff só quando a base não divergiu) e informa o novo SHA de base. Rejeitada → Claude envia correções objetivas na mesma tarefa.

## Registro de delegações (evidência)

| Data | Tarefa | Enviada a | ID da mensagem | SHA base | Resultado |
|---|---|---|---|---|---|
| 2026-11-27 | coordenação inicial | Implementador | resposta `msg_9c1988924a3f` | `5e49d39` | Codex confirmou alinhamento da branch em `5e49d39` |
| 2026-11-27 | T-001 | Implementador | `msg_aca8ae24b297` | `c5b9e6f` | Entregue `4655036`; aceita, integrada em `25f87b5` |
| 2026-11-27 | T-007 | Implementador | `msg_06e351323811` | `99c9a04` | Entregue `620eb34`; aceita, integrada em `d2d94e5` |
| 2026-11-27 | T-003 | Implementador | `msg_bd7d585725d7` | `3b1fe9a` | Entregue `eb400ce`; aceita, integrada em `b10b3ce` |
| 2026-11-27 | T-002 | Implementador | `msg_c784fcbf05f9` | `651f1b4` | Entregue `603a667` (rebaseada em `644cbf8`); aceita, integrada em `fc545f1` |

(Novas linhas são adicionadas a cada `send`/entrega. Uma tarefa só consta como delegada com o ID de mensagem aqui.)

## Limitações conhecidas

- O terminal do Codex não é um worker gerenciado (`worker-start`): sem `worker_done` automático; a conclusão é por mensagem. Se a mensagem não chegar, o estado real é verificado pelo `git log` da branch dele.
- Entrega por terminal não é durável; reenviar a partir deste arquivo se necessário.
