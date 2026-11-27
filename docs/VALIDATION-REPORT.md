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
| Mesmo comando com `TEMP`/`TMP` em `C:\brfc-nonexistent-xyz` | 17 OK |
| `git status` após testes; conteúdo residual em `.test-tmp/` | limpo; 0 itens |
| CLI da demo (`examples/`) | saída 1; totais `2850.00` / `9000.00` / `2650.00` |

Ressalvas: (a) a falha de permissão original não foi reproduzida pelo Codex; (b) o helper é importado como `from support import ...`, o que funciona com `discover -s tests` (comando do CI e do projeto) mas não com `python -m unittest tests.test_review` a partir da raiz; (c) execução no sandbox do Codex com a falha original continua não comprovada.

### T-007 — testes de CLI e casos extremos · `620eb34` (integrada em `d2d94e5`)
Escopo: somente `tests/test_cli.py` (68 linhas) e `tests/test_edge_cases.py` (135 linhas); motor e testes existentes intocados (`git diff --stat`).

| Verificação (árvore do Claude, pós-merge) | Resultado |
|---|---|
| `python -m unittest discover -s tests` | 28 testes: 27 OK + 1 `expectedFailure`; 0,6 s |
| Com `TEMP`/`TMP` inexistentes | idem |
| `git status`; resíduo em `.test-tmp/` | limpo; 0 itens |
| `expectedFailure` rodado sem o decorator | falha com `AssertionError` (confirma que não mascara) |

`expectedFailure` registrado: `test_csv_finding_uses_physical_line_after_multiline_record` — achados numeram registros lógicos (`[2,3]`), não linhas físicas (`[2,4]`) após campo multilinha. Corresponde ao achado B-10; correção prevista na **T-004** (o teste passa a ser normal). Observação: o contrato atual documenta "registros", então a mudança para linha física é alteração de comportamento a constar no CHANGELOG.

Cobertura nova: códigos de saída 0/1/2/3 e ausência de relatório no 3; determinismo byte a byte; não-eco de entrada; limites de dinheiro/datas/vigência; tolerância (despesa, líquido e pago da folha); contrato da política; cabeçalhos e linhas malformadas; BOM, CRLF, campo vazio, só cabeçalho, multilinha; limite de 100000 linhas.
Lacunas conhecidas: sem teste de dígitos Unicode em datas/competência (coberto só em dinheiro) e sem teste de `paid > gross` isolado; ficam para a T-004.

### T-003 — exemplos dentro do plugin · `eb400ce` (integrada em `b10b3ce`)
Escopo (`git diff -M --stat`): 4 renames 100% `examples/` → `plugins/.../skills/br-financial-compliance/examples/`; caminhos atualizados em README PT/EN, CI, `.gitignore`, `docs/DATA-CONTRACT.md`, 3 arquivos de teste; CHANGELOG (seção Unreleased); novo `tests/test_references.py`. Extra declarado pelo Codex: ajuste textual em `docs/TECHNICAL-AUDIT.md` (menção histórica virou prosa) — aceito.

| Verificação (árvore do Claude, pós-merge) | Resultado |
|---|---|
| `python -m unittest discover -s tests` (normal e com `TEMP`/`TMP` inexistentes) | 29 testes: 28 OK + 1 `expectedFailure` (o de T-004) |
| `git ls-files \| grep examples` | 4 arquivos, só no novo local; `examples/` da raiz não existe |
| SHA-256 dos 4 arquivos, v0.1.0 vs atual (ignorando fim de linha) | idênticos |
| Mutação: acrescentar ao README a citação de um CSV inexistente na pasta de exemplos da skill | `test_references` falha apontando o arquivo e a referência; README restaurado, árvore limpa |
| Comando de demonstração copiado do README, executado da raiz | saída 1; totais `2850.00` / `9000.00` / `2650.00` |

Ressalvas: o comando de demonstração ficou longo (caminho completo do plugin); o `.gitignore` agora tem exceção específica ao caminho novo (um CSV novo em outro lugar continua ignorado, como desejado). `python -m unittest tests.test_references` (módulo a partir da raiz) falha por import, igual à ressalva da T-001; o comando oficial é `discover -s tests`.

### T-002 — build reprodutível e validação do plugin · `603a667` (integrada em `fc545f1`)
Escopo (`git diff --stat`): `scripts/build_release.py` (84 linhas), `scripts/validate_plugin.py` (86), `tests/test_packaging.py` (76), `.github/workflows/tests.yml`, `.gitignore` (`dist/`). Nenhum arquivo fora do previsto; motor, testes anteriores e exemplos intocados. Só biblioteca padrão.

| Verificação (árvore do Claude, pós-merge) | Resultado |
|---|---|
| `python -m unittest discover -s tests` (normal e `TEMP`/`TMP` inexistentes) | 31 testes: 30 OK + 1 `expectedFailure` (T-004) |
| `python scripts/validate_plugin.py` | saída 0 |
| Build duplo em `dist/a` e `dist/b` | `SHA256SUMS` idênticos; skill `cdd1d4a7…db602`, plugin `0045a693…681e2` |
| Hashes do Claude vs. hashes informados pelo Codex (outra worktree) | idênticos |
| Segundo build no mesmo destino | falha (`Output already exists`), saída 1, nada alterado |
| Conteúdo dos ZIPs | skill 11 arquivos, plugin 14; datas fixas 2026-01-01, permissões 0644; sem CRLF; sem `__pycache__`/`.pyc`/`demo-report`/`reports`; skill com `examples/` |
| ZIP da skill extraído, demo executada com os exemplos extraídos | saída 1; totais `2850.00` / `9000.00` / `2650.00` |
| `git status`, `dist/` removido | limpo |

**Não verificado:** o CI hospedado (matriz Ubuntu/Windows × Python 3.10/3.12) — o workflow foi escrito, não executado; não há alegação de aprovação. Python 3.10 não foi exercitado localmente (só 3.12).
**Limites conhecidos:** (1) a igualdade de hash comprova reprodutibilidade na mesma versão de zlib; ZIPs gerados em máquinas com zlib diferente podem divergir nos bytes comprimidos mesmo com conteúdo idêntico — o CI só compara dois builds no mesmo runner; (2) o build lê a árvore de trabalho dos arquivos versionados, então alterações locais não commitadas entram no ZIP; (3) `validate_plugin.py` só checa referências entre crases em `SKILL.md` e `references/*.md`.
