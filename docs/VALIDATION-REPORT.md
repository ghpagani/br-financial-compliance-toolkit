# Relatório de validação

Registro cronológico de evidências. Só entram aqui comandos efetivamente executados.

## 2026-11-27 — Base v0.1.0 (`5e49d39`), máquina do mantenedor (Windows 11, Python 3.12.10)

| Verificação | Comando | Resultado |
|---|---|---|
| Testes unitários | `python -m unittest discover -s tests -v` | 16 testes, OK (0,049 s) |
| Estado do Git | `git status` | limpo |
| Sondagens de casos extremos | script no scratchpad (fora do repo), `python -I -X utf8` | ver `TECHNICAL-AUDIT.md` §4 |

Não verificado nesta rodada: execução em sandbox do Codex (A-01), CI no GitHub, Ubuntu/Python 3.10, links externos.

## Validações anteriores informadas pelo mantenedor (não reexecutadas por Claude)

PowerShell 16 OK; GitHub Actions OK; Claude Code/Orca 16 OK; Claude Online com base fictícia (19 achados, 4 bloqueios); Codex 13 OK e 3 erros de permissão em diretório temporário.

## Entregas revisadas

### T-001 — testes sem temp do sistema · `4655036` (integrada em `25f87b5`)
Escopo conferido por `git diff --stat`: `.gitignore`, `tests/support.py`, `tests/test_review.py` (3 arquivos); nenhuma asserção existente alterada; `review.py` intocado.

| Verificação (árvore do Claude, pós-merge) | Resultado |
|---|---|
| `python -m unittest discover -s tests` | 17 testes OK (16 originais + 1 do helper) |
| Mesmo comando com `TEMP`/`TMP` em `C:rfc-nonexistent-xyz` | 17 OK |
| `git status` após testes; conteúdo residual em `.test-tmp/` | limpo; 0 itens |
| CLI da demo (`examples/`) | saída 1; totais `2850.00` / `9000.00` / `2650.00` |

Ressalvas: (a) a falha de permissão original não foi reproduzida pelo Codex; (b) o helper é importado como `from support import ...`, o que funciona com `discover -s tests` (comando do CI e do projeto) mas não com `python -m unittest tests.test_review` a partir da raiz; (c) execução no sandbox do Codex com a falha original continua não comprovada.
