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

(nenhuma ainda — T-001 em diante serão registradas aqui com SHA, comando e resultado)
