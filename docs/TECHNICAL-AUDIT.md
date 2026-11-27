# Auditoria técnica — BR Financial Compliance Toolkit (base v0.1.0)

Data: 2026-11-27 · Base auditada: commit `5e49d39` (main do repositório original) · Autor: Claude (líder técnico)
Status: **Fase 1 parcialmente concluída** (itens marcados "pendente" na seção 7).
Natureza: apoio à decisão técnica; não é parecer contábil, jurídico ou de auditoria.

## 1. Escopo e método

- Leitura integral de `review.py` (215 linhas), `tests/test_review.py` (57 linhas), manifestos, CI, `.gitignore`, fixtures e documentação-chave.
- Execução dos testes: `python -m unittest discover -s tests -v` → **16 testes, OK** (Python 3.12.10, Windows 11).
- Sondagens de casos extremos com dados sintéticos, scripts no scratchpad (fora do repositório).
- Comparação da skill instalada em `~/.claude/skills/br-financial-compliance` com o plugin do repositório.
- Leitura de ADR001/003/010 e estrutura do clone local da Calculadora RTC (último commit local `150cccb`, 2026-10-22).

## 2. Achado estrutural: workspace do Orca vazio

O worktree do Orca partia de um commit inicial **vazio** (`a3152a3`, 0 arquivos, sem remoto). O código real estava em
`C:\Users\ghpag\Documents\Claude\GitHub\br-financial-compliance-toolkit` (main = `5e49d39`, remoto GitHub `ghpagani/br-financial-compliance-toolkit`).
Ação: `git fetch` local (somente leitura na origem) e realinhamento das duas branches vazias (`ghpagani/br-financial-compliance-toolkit` e `ghpagani/Implementador`) para `5e49d39`. Nenhum trabalho foi perdido (ambas tinham só o commit vazio). Ver DECISIONS D-001.

## 3. Pontos fortes (com evidência)

| # | Ponto | Evidência |
|---|---|---|
| F1 | Dinheiro em `Decimal` com entrada canônica rígida (sem float, expoente, vírgula, NaN) | `money()`; `test_invalid_money` |
| F2 | Dígitos Unicode não-ASCII rejeitados em dinheiro, data e competência | sondagem: `'٢٠٢٦-…'` → `ValueError` |
| F3 | Relatório determinístico (sem timestamp), sem eco de entrada nos erros | leitura de `invalid()` |
| F4 | Saída nunca sobrescreve (`open(..., 'x')`) | `test_no_overwrite` |
| F5 | Escopo declarado e limitações no próprio relatório | chave `limitations` |
| F6 | Tolerância limitada a 0,01 e validada | `policy_load` |

## 4. Achados e riscos

Severidade: **A** alta, **M** média, **B** baixa. IDs referenciados no backlog.

| ID | Sev | Achado | Evidência | Tarefa |
|---|---|---|---|---|
| A-01 | A | 3 testes dependem de `TemporaryDirectory()` no temp do sistema (`C:\Users\…\AppData\Local\Temp`); no sandbox do Codex esse diretório não é gravável → os 3 erros relatados. Causa por leitura de código; o Codex **não reproduziu** a falha no ambiente dele (16 testes originais passaram); causa não confirmada, dependência removida na T-001 | `test_invalid_schema`, `test_policy_explicit`, `test_no_overwrite` | T-001 |
| A-02 | A | O plugin distribuído **não contém** `examples/`; `data-contract.md` (dentro da skill) manda ler `examples/policy.json`, que só existe na raiz do repositório. Instalação via marketplace copia só `plugins/…` | `find plugins`; grep em `data-contract.md:21` | T-003 |
| A-03 | A | Não há geração de ZIP; nada garante reprodutibilidade, exclusão de `__pycache__` (existe `scripts/__pycache__/*.pyc` no diretório do plugin, ignorado pelo Git mas que entraria num ZIP manual) nem normalização de fim de linha (`core.autocrlf=true` nesta máquina gera CRLF) | `find plugins` | T-002 |
| M-04 | M | Falha na gravação após `open(..., 'x')` deixa relatório **parcial** no disco (JSON truncado) | leitura de `main()`; apontado também pelo Codex | T-004 |
| M-05 | M | `INPUT_INVALID` não diz **por quê** (duplicidade de id, moeda, período, `deductions>gross`, data inválida, flag inválido). Rastreabilidade fraca: linha aponta, causa não | sondagem: `dup id` e `ded>gross` → mesma mensagem genérica | T-004 |
| M-06 | M | Duplicidade só por `(vendor, invoice)`. Mesmo fornecedor, valor e data com NF diferente não é sinalizado | sondagem `near-dup` → só `EXP_BUDGET_UNMATCHED` | T-004 |
| M-07 | M | Sem memória de cálculo estruturada: achados trazem `expected/actual/difference`, mas não fórmula, tolerância aplicada nem arredondamento | leitura de `add()` | T-005 |
| M-08 | M | Mensagens apenas em inglês; sem relatório legível (Markdown) | leitura | T-006 |
| M-09 | M | Cobertura de testes: não há teste do CLI para códigos de saída 0/1/2/3 (só o 3), CSV malformado, BOM, limites de dinheiro, bordas de tolerância e arredondamento | `test_review.py` | T-007 |
| B-10 | B | `i` em `read_csv` é o índice de registro + 1, não o número físico da linha; campos entre aspas com quebra de linha deslocam o número reportado (`reader.line_num` é o correto) | leitura de `read_csv` | T-004 |
| B-11 | B | `import calendar` dentro do laço de folha | leitura | T-004 |
| B-12 | B | `ctx.prec=40` só é aplicado em `main()`; chamadas diretas a `review()` usam precisão 28. Sem impacto hoje (máx. 16 dígitos), mas é uma armadilha de API | leitura | T-004 |
| B-13 | B | CI só roda no Ubuntu; o uso real é Windows (e Orca). Sem job de empacotamento | `tests.yml` | T-002 |
| B-14 | B | `demo-report.json` e `reports/` existem no diretório original (ignorados pelo Git); sem risco, mas convém não os empacotar | `ls` do original | T-002 |

Confirmado **sem defeito** nas sondagens: `paid > gross` é sinalizado (simétrico); fronteira de tolerância (diferença 0,01 aceita; 0,02 sinalizada); `99999999999999.99` aceito; `0` aceito; ids duplicados excluem ambas as linhas.

## 5. Referência arquitetural (Receita Federal, calculadora RTC)

Lido nesta fase: ADR001 (cálculo por expressão), ADR003 (precisão numérica), ADR010 (observabilidade) — via citações já registradas em `references/sources.md`; leitura integral dos ADRs 001/003/010 e do esquema Flyway: **pendente** (T-010). Princípios aplicáveis ao toolkit, sem copiar código ou tabelas:

1. Regras versionadas e com vigência, separadas do motor.
2. Aritmética decimal com precisão e arredondamento explícitos e documentados.
3. Memória de cálculo por item; erro por item, não falha global.
4. Execução local e rastreável.

A RTC cobre CBS/IBS/IS (consumo) e **não** encargos de folha; o toolkit não deve misturá-los (já registrado em `SOURCES.md`).
Validade das referências: o clone local tem último commit em 2026-10-22; a atualização (`git pull`) e a conferência de vigência em fonte oficial ficam pendentes e **exigem rede** (T-010).

## 6. Divergência verificada: skill instalada vs. repositório

Conteúdo idêntico ao do repositório; difere apenas o fim de linha (CRLF na cópia instalada). Sem ação no repositório. A cópia instalada é configuração do usuário e não foi alterada.

## 7. Pendências da Fase 1

- Reproduzir A-01 dentro do sandbox do Codex (feito pelo Implementador em T-001).
- Leitura completa dos ADRs e de `flyway/sql` da RTC (T-010).
- Validar que os links de `docs/SOURCES.md` e `references/sources.md` continuam acessíveis (requer rede; T-010).
- Revisão completa de `docs/*.md`, `SECURITY.md`, `CONTRIBUTING.md` e licenças (T-008).

## 8. Conclusão

O núcleo é pequeno, determinístico e conservador; a base é adequada para evoluir. Os riscos relevantes da v0.1.0 são de **distribuição** (A-02, A-03), **testabilidade em sandbox** (A-01) e **rastreabilidade** (M-04…M-07), não de aritmética. Nenhum achado indica erro de cálculo nos 16 cenários cobertos; isso não equivale a certificação.
