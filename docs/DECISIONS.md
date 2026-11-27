# Registro de decisões

| ID | Data | Decisão | Motivo | Impacto |
|---|---|---|---|---|
| D-001 | 2026-11-27 | O worktree do Orca (commit vazio `a3152a3`) foi realinhado para `5e49d39` via `git fetch` do diretório local original; o original não foi modificado. Idem a branch `ghpagani/Implementador`. | Workspace vazio e sem remoto; a origem tem a v0.1.0 limpa | Nenhuma perda (as branches só tinham o commit vazio). Sem push |
| D-002 | 2026-11-27 | Testes não usam o temp do sistema; usam `<repo>/.test-tmp/` (gitignored) | Sandbox do Codex não grava em `%TEMP%`; não se desabilita controle de segurança | T-001 |
| D-003 | 2026-11-27 | Exemplos canônicos migram para dentro da skill (`.../skills/br-financial-compliance/examples/`); `examples/` da raiz é removido; sem symlinks | Instalação via marketplace copia só `plugins/…`; evitar duas cópias divergentes | Mudança de caminho em README/CI/testes (documentada no CHANGELOG). Conteúdo dos arquivos inalterado |
| D-004 | 2026-11-27 | Campos novos nos relatórios são aditivos; `--lang`/`--format` com padrão `en`/`json` | Compatibilidade com v0.1.0 | T-004…T-006 |
| D-005 | 2026-11-27 | ZIP reproduzível a partir de `git ls-files`, LF normalizado, data fixa, hashes publicados | `core.autocrlf` e `__pycache__` tornam ZIP manual não reproduzível | T-002 |
| D-006 | 2026-11-27 | Nenhuma regra legal executável na v0.1.1/v0.2.0 sem fonte primária e validação profissional | Instrução do projeto e skill `br-financial-compliance` | Fase 4 |
| D-007 | 2026-11-27 | Importação de Excel só após decisão humana sobre dependência | Regra do projeto: não instalar bibliotecas sem perguntar | Bloqueio M2 |
