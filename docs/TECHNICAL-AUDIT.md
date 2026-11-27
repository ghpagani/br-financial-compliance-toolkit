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
| A-02 | A | O plugin distribuído **não contém** `examples/`; `data-contract.md` (dentro da skill) manda ler `policy.json` na pasta de exemplos, que só existe na raiz do repositório. Instalação via marketplace copia só `plugins/…` | `find plugins`; grep em `data-contract.md:21` | T-003 |
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

Leitura feita em 2026-11-27 sobre o clone local, atualizado por `git pull --ff-only` de `150cccb` (2026-10-22) para **`0d4b073` (2026-11-26, tag 1.7.3)**: ADR001, 003, 007, 009 e 010 integralmente; ADR011 (Spring Boot 4/Java 25, sem relação com o toolkit); estrutura de `flyway/sql`; `MemoriaCalculoDomain`. Nada foi executado (sem `mvnw`) e nenhum código ou tabela foi copiado.

**Achado de vigência:** o clone estava defasado (6 commits; releases 1.7.2 e 1.7.3) e o **ADR003 foi reescrito em 17/11/2026**. O princípio que o toolkit citava ("aritmética decimal precisa") segue verdadeiro, mas o conteúdo mudou e é mais específico. Registro atualizado em `docs/SOURCES.md` e `references/sources.md`.

| Tema | O que a RTC faz (fonte) | Toolkit hoje | Ação |
|---|---|---|---|
| Arredondamento | Conta interna exata; **um** arredondamento por número publicado; modo único `HALF_EVEN` "convenção do projeto; não há dispositivo legal que fixe o modo"; classe única protegida por teste de arquitetura e SHA-256; somas sobre os valores publicados (ADR003) | v0.1.x só soma/subtrai valores de 2 casas: **nenhum arredondamento** (verificado, T-005) | v0.2.0: ao entrarem alíquotas, módulo único de arredondamento, modo declarado **por regra**, nunca presumido como exigência legal; teste de arquitetura "sem arredondamento fora do módulo"; definir por regra se o valor publicado alimenta a conta seguinte (D-008) |
| Erro por item | Erros estruturados (tipo, campo, detalhe); item com erro sai do total "sem aviso explícito no nível da operação" (ADR010) | `reason`+`field` (T-004); `coverage` e `limitations` declaram exclusões | Já atende e é mais explícito; manter |
| Regras em dados | Expressões JEXL no banco, com sandbox (ADR001) | — | v0.2.0 M1: regras declarativas versionadas; **não** avaliar expressões arbitrárias (superfície de ataque); fórmulas nomeadas e parametrizadas (D-009) |
| Versionamento e vigência | Scripts `B####`/`V####` com checksum; registro obrigatório de versão da base; vigência por colunas de data início/fim (ADR009, `flyway/sql`) | Esquema de regra prevê versão, vigência e histórico (`RULE-REGISTRY.md`) | M1: carregador rejeita regra sem versão, vigência ou histórico; testes de vigência por data |
| Memória de cálculo | Texto livre por tributo (`cbs`, `ibsUF`, `ibsMun`) | `calculation` estruturado e recomputável (T-005) | Superior em verificabilidade; manter |

Escopo: a RTC cobre CBS/IBS/IS (consumo) e **não** encargos de folha; não é base de cálculo para INSS/IRRF/FGTS.

## 6. Divergência verificada: skill instalada vs. repositório

Conteúdo idêntico ao do repositório; difere apenas o fim de linha (CRLF na cópia instalada). Sem ação no repositório. A cópia instalada é configuração do usuário e não foi alterada.

## 7. Pendências da Fase 1

- ~~Reproduzir A-01 no sandbox do Codex~~ — não reproduzido pelo Codex; dependência removida (T-001).
- ~~Leitura dos ADRs e de `flyway/sql` da RTC~~ — feita (seção 5; T-010).
- Links de `docs/SOURCES.md` e demais documentos: 14 de 16 verificados (HTTP 200; GitHub ADR001/003 deram 503 e passaram no retry). **Os 2 links do Planalto (CLT, LGPD) não responderam desta máquina** (timeout de 25 s e 60 s, inclusive a página inicial): **não verificados**, não necessariamente inválidos. O registro afirma "verified 2026-11-27" para a LGPD; essa verificação **não foi reproduzida** aqui.
- Revisão completa de `README*`, `SECURITY.md`, `CONTRIBUTING.md`, `INSTALL.md` e licenças (T-008, pendente).

## 7b. Estado dos achados ao fim da v0.1.1 (2026-11-27)

| ID | Estado | Resolução e ressalva |
|---|---|---|
| A-01 testes dependiam do temp do sistema | Mitigado; causa **não confirmada** | T-001. O Codex não reproduziu a falha original no sandbox dele |
| A-02 plugin sem `examples/` | Resolvido | T-003; `test_references` e `validate_plugin` impedem regressão |
| A-03 sem ZIP reproduzível | Resolvido, com ressalva | T-002; hashes idênticos em 3 builds/clones; vale para a mesma zlib; CI **não executado** |
| M-04 relatório parcial em falha de gravação | Resolvido | T-004; falhas injetadas (`json.dump`, `os.link`) sem resíduo. Exige volume com hard link (documentado) |
| M-05 rejeição sem motivo | Resolvido | T-004 (`reason`/`field`); contrato documenta os 11 valores e um teste os mantém iguais ao código |
| M-06 quase-duplicidade | Resolvido | T-004 (`EXP_POSSIBLE_DUPLICATE_AMOUNT`); ruído conhecido em grupos {A,A,B} |
| M-07 sem memória de cálculo | Resolvido | T-005; recomputação independente de 18755 achados sem divergência |
| M-08 só inglês, sem Markdown | Resolvido | T-006/6b/6c; escape verificado por inspeção do texto gerado, **não** por renderização |
| M-09 cobertura de testes | Resolvido | de 16 para 62 testes |
| B-10 número de linha | Resolvido | T-004; muda só para CSV com campo multilinha (no CHANGELOG) |
| B-11, B-12 | Resolvidos | T-004 |
| B-13 CI só no Ubuntu | **Parcial** | workflow com Ubuntu/Windows × 3.10/3.12 escrito, **nunca executado**; 3.10 só verificado estaticamente |
| B-14 artefatos locais no pacote | Resolvido | build usa `git ls-files` |

Achados novos durante o desenvolvimento: autolinks e caracteres bidi/separadores no Markdown (corrigidos em T-006b/c); teste que estourava `MAX_PATH` no Windows em caminho profundo (corrigido, achado por clone limpo); afirmação "verified" da LGPD no registro de fontes não reproduzível (corrigida); links do Planalto não verificáveis nesta máquina (aberto).

## 8. Conclusão

O núcleo é pequeno, determinístico e conservador; a base é adequada para evoluir. Os riscos relevantes da v0.1.0 são de **distribuição** (A-02, A-03), **testabilidade em sandbox** (A-01) e **rastreabilidade** (M-04…M-07), não de aritmética. Nenhum achado indica erro de cálculo nos 16 cenários cobertos; isso não equivale a certificação.
