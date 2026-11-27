# Backlog de desenvolvimento

Atualizado: 2026-11-27 · Base: `5e49d39` · Líder/revisor: Claude · Implementador: Codex (terminal Orca `Implementador`, branch `ghpagani/Implementador`)

## Regras de coordenação

1. **Um dono por arquivo.** Tarefas que tocam `review.py` são sequenciais. Nenhum agente edita arquivo de outra tarefa em andamento.
2. Fluxo: Codex implementa na branch `ghpagani/Implementador` com commits focados (um por tarefa) → informa o SHA → Claude revisa o diff, roda os testes e registra evidência em `docs/VALIDATION-REPORT.md` → Claude integra na branch `ghpagani/br-financial-compliance-toolkit` (fast-forward ou merge) → próxima tarefa parte do novo SHA.
3. Sem push, sem merge na `main`, sem release (exige autorização humana).
4. Sem desabilitar sandbox, sem elevar privilégios, sem dados reais. Comandos: `python -m unittest discover -s tests -v`.
5. Mudança de comportamento só com teste que a descreva **e** entrada no CHANGELOG. Nunca ajustar um cálculo para um teste passar.
6. Compatibilidade: campos novos nos relatórios são **aditivos**; `code`, `severity`, `row`, `module`, `expected`, `actual`, `difference`, códigos de saída 0/1/2/3 e os totais da demo (`2850.00` / `9000.00` / `2650.00`) permanecem.

## Quadro de tarefas v0.1.1

Legenda de status: `A fazer` · `Delegada` · `Em revisão` · `Aceita` · `Bloqueada`.

| ID | Objetivo | Responsável | Depende de | Status |
|---|---|---|---|---|
| T-001 | Testes compatíveis com sandbox (sem temp do sistema) | Codex | — | A fazer |
| T-007 | Testes de CLI, CSV malformado/Unicode e casos extremos | Codex | T-001 | A fazer |
| T-003 | Exemplos e política dentro do plugin; corrigir referências | Codex | T-001 | A fazer |
| T-002 | ZIP reproduzível + validação de estrutura do plugin + CI | Codex | T-003 | A fazer |
| T-004 | Endurecimento do motor: motivos de rejeição, quase-duplicidade, gravação atômica | Codex | T-001, T-007 | A fazer |
| T-005 | Memória de cálculo estruturada | Codex | T-004 | A fazer |
| T-006 | Relatórios PT/EN e saída Markdown | Codex | T-005 | A fazer |
| T-008 | Documentação, licenças, atribuições, versão 0.1.1, CHANGELOG | Claude | T-002, T-006 | A fazer |
| T-009 | Governança: RULE-REGISTRY e esquema de regra (sem regra legal) | Claude | — | Em andamento |
| T-010 | Leitura integral dos ADRs/Flyway da RTC; verificar links e vigência (requer rede) | Claude | — | A fazer |

Ordem de execução do Codex: **T-001 → T-007 → T-003 → T-002 → T-004 → T-005 → T-006**. T-007 e T-003 tocam arquivos distintos após T-001, mas há um só implementador; a ordem acima prioriza rede de segurança de testes antes de mexer no motor.

---

## T-001 — Testes compatíveis com o sandbox do Codex

- **Objetivo:** eliminar a dependência do diretório temporário do sistema nos testes.
- **Causa provável (A-01):** `TemporaryDirectory()` grava em `%TEMP%`, bloqueado no sandbox do Codex.
- **Escopo:** apenas a infraestrutura de teste. Não alterar `review.py`.
- **Arquivos:** `tests/test_review.py`, novo `tests/support.py` (helper), `.gitignore` (adicionar `.test-tmp/`).
- **Abordagem:** helper que cria um diretório único em `<raiz do repo>/.test-tmp/<uuid>` (gitignored), usado como gerenciador de contexto e removido ao final; permitir override por variável `BRFC_TEST_TMP`. Proibido: `tempfile` sem `dir=`, `chmod`, mudar `TEMP`/`TMP` globalmente.
- **Critérios de aceitação:**
  1. `python -m unittest discover -s tests -v` → 16 testes OK, sem escrever fora do repositório (comprovar com `TMP`/`TEMP` apontando para um diretório inexistente: ainda 16 OK).
  2. `git status` limpo após a execução (`.test-tmp/` ignorado e removido).
  3. Nenhum teste existente tem sua asserção alterada.
- **Casos de teste:** os 3 existentes (`test_invalid_schema`, `test_policy_explicit`, `test_no_overwrite`) rodam com o helper; adicionar 1 teste do próprio helper (cria e remove o diretório).
- **Riscos:** limpeza falha no Windows por handle aberto → usar `shutil.rmtree` após fechar arquivos.

## T-007 — Testes de CLI, entradas malformadas e casos extremos

- **Objetivo:** rede de segurança antes de alterar o motor.
- **Arquivos:** novo `tests/test_cli.py`, novo `tests/test_edge_cases.py`. Não alterar `review.py` (se um teste revelar defeito, **não corrigir**: marcar `@unittest.expectedFailure` com comentário `# T-004` e reportar).
- **Critérios de aceitação:** cobrir, no mínimo:
  - `main()` retorna 0 (sem achados), 1 (achados de revisão), 2 (bloqueio), 3 (E/S/esquema) — por exemplo, via arquivos sintéticos mínimos;
  - CSV: cabeçalho duplicado/ausente/extra, linha com colunas a mais/a menos, BOM, CRLF, campo vazio, arquivo vazio só com cabeçalho, limite de 100000 linhas (100001 → erro), aspas com quebra de linha;
  - Dinheiro: `0`, `0.00`, `99999999999999.99`, `100000000000000.00` (rejeita), `.5`, `5.`, `+1`, espaços, dígitos Unicode;
  - Datas: `2026-02-29`, `2026-02-30`, `2026-13-01`, fronteiras da vigência (primeiro/último dia), competência parcial;
  - Tolerância: diferença 0,00 / 0,01 / 0,02 em despesas e folha; `paid > gross`;
  - Política: chaves extras/ausentes, `tolerance` `0.02`, `currency` `USD`, datas invertidas;
  - Determinismo: duas execuções com a mesma entrada geram JSON byte a byte idêntico;
  - Saída: o relatório não contém dados de entrada arbitrários (ex.: valor de `project` malicioso é rejeitado, não ecoado).
- **Riscos:** testes frágeis por mensagem de texto → asserir `code`/`severity`/`row`, não `message`.

## T-003 — Exemplos e política dentro do plugin

- **Objetivo:** o pacote instalado funciona sozinho e não referencia arquivos ausentes (A-02).
- **Decisão (D-003):** a cópia canônica passa a ficar em `plugins/br-financial-compliance/skills/br-financial-compliance/examples/` (`policy.json`, `expenses.csv`, `payroll.csv`, `budgets.csv`). `examples/` na raiz é **removido**; sem symlinks (Windows).
- **Arquivos:** mover os 4 arquivos (`git mv`); atualizar caminhos em `tests/*`, `.github/workflows/tests.yml`, `README.md`, `README.pt-BR.md`, `docs/INSTALL.md`, `docs/DATA-CONTRACT.md`, `AGENTS.md`, `.gitignore` (`!examples/*.csv` → caminho novo; `demo-report*.json` mantido) e as referências em `references/*.md` e `SKILL.md`.
- **Critérios de aceitação:**
  1. Todos os testes passam com os novos caminhos; conteúdo dos 4 arquivos **byte a byte inalterado**.
  2. `grep -rn "examples/"` em docs/código só encontra caminhos que existem (adicionar teste que varre `*.md` e `*.json` do repositório e falha se um caminho `examples/...` citado não existir relativamente à raiz da skill ou do repositório).
  3. Comando de demonstração do README, executado do zero, retorna código 1 e reproduz os totais.
- **Riscos:** o `.gitignore` ignora `*.csv`; conferir com `git status` que os 3 CSV continuam rastreados.

## T-002 — ZIP reproduzível, validação de estrutura e CI

- **Objetivo:** gerar artefatos de distribuição de forma automatizada e verificável (A-03, B-13, B-14).
- **Arquivos:** novo `scripts/build_release.py`, novo `scripts/validate_plugin.py`, novo `tests/test_packaging.py`, `.github/workflows/tests.yml`.
- **Requisitos do `build_release.py`:** somente biblioteca padrão; entrada: lista de arquivos **rastreados pelo Git** (`git ls-files`) dentro de `plugins/br-financial-compliance/` — nunca varrer o disco; excluir `__pycache__`, `*.pyc`; ordenar caminhos; `ZipInfo` com data fixa `(2026,1,1,0,0,0)`, permissões fixas, `ZIP_DEFLATED` nível fixo; **normalizar fim de linha para LF** em arquivos de texto; saída em `dist/` (gitignored), sem sobrescrever (falha se existir, `--force` não deve existir); gerar também `SHA256SUMS`. Dois ZIPs: `br-financial-compliance-skill-<versão>.zip` (somente a pasta da skill, com `SKILL.md` na raiz do zip) e `br-financial-compliance-plugin-<versão>.zip` (pasta do plugin). Versão lida de `plugin.json` e verificada contra `VERSION` de `review.py`.
- **Requisitos do `validate_plugin.py`:** valida JSON dos dois `plugin.json` e dos dois `marketplace.json`; `name` e `version` coerentes entre si e com `review.py`; `SKILL.md` com front matter (`name` igual ao diretório, `description` não vazia); todo caminho citado em `SKILL.md`/`references` existe; `LICENSE` presente no plugin e na skill; exemplos presentes; nenhum `.csv`/`.json` fora de `examples/` e dos manifestos; saída com código ≠ 0 em qualquer falha.
- **Critérios de aceitação:**
  1. Construir duas vezes (em diretórios de saída distintos) produz ZIPs com **SHA-256 idêntico**.
  2. Conteúdo do ZIP = exatamente os arquivos rastreados esperados (teste compara lista); sem `.pyc`, sem `demo-report*.json`, sem `reports/`; contém `examples/`.
  3. Extrair o ZIP da skill em diretório do repositório gitignored e executar o `review.py` com `examples/` extraídos → código 1 e mesmos totais.
  4. Teste negativo: manifesto com versão divergente faz o validador falhar.
  5. CI: matriz com `ubuntu-latest` e `windows-latest`, Python 3.10 e 3.12; passos: testes, validação, build, verificação de hash duplo. `permissions: contents: read`; actions fixadas por versão como hoje.
- **Riscos:** `git ls-files` ausente em ambiente sem Git → falhar com mensagem clara, não degradar para varredura.

## T-004 — Endurecimento do motor (`review.py`)

- **Objetivo:** rastreabilidade das rejeições, melhor detecção e gravação segura (M-04, M-05, M-06, B-10…B-12).
- **Arquivos:** somente `review.py` e testes novos/ajustados; docs da skill que descrevam os campos novos (`references/data-contract.md`, `references/controls.md`).
- **Mudanças (todas aditivas):**
  1. **Motivo da rejeição:** `INPUT_INVALID` ganha campo `reason` com valor de um conjunto fechado (literais fixos, **nunca** texto da entrada): `HEADER`, `MALFORMED_ROW`, `DUPLICATE_ID`, `CURRENCY`, `OUT_OF_PERIOD`, `PARTIAL_COMPETENCE`, `INVALID_DATE`, `INVALID_AMOUNT`, `INVALID_REFERENCE`, `INVALID_FLAG`, `INVALID_PAYROLL`, `INVALID_BUDGET_DATES`. Também o campo `field` quando aplicável (nome da coluna do contrato).
  2. **Quase-duplicidade:** nova regra `EXP_POSSIBLE_DUPLICATE_AMOUNT` (REVIEW): mesmo `vendor` + `paid` + `date`, `invoice` diferente. Não deve duplicar o achado quando já há `EXP_POSSIBLE_DUPLICATE` para o mesmo par de linhas. Registrar em `docs/RULE-REGISTRY.md`.
  3. **Gravação segura:** escrever em arquivo temporário no mesmo diretório e publicar sem sobrescrever (`os.link` + remoção do temporário, ou equivalente que falhe se o destino existir e funcione no Windows); em qualquer falha, **nenhum** arquivo parcial permanece. Manter código de saída 3 e a mensagem.
  4. **Número de linha** físico via `reader.line_num` (B-10); mover `import calendar` ao topo (B-11); aplicar `localcontext(prec=40)` dentro de `review()` (B-12).
- **Critérios de aceitação:** os 16 testes originais passam sem alteração de asserção; os `expectedFailure` de T-007 que correspondem a estes itens passam a ser removidos e viram testes normais; novo teste simula falha de gravação (ex.: `json.dump` levantando `OSError` via monkeypatch) e verifica que o destino não existe; totais da demo inalterados; JSON da demo difere do anterior **somente** por campos novos.
- **Riscos:** `EXP_POSSIBLE_DUPLICATE_AMOUNT` pode gerar ruído em parcelas legítimas → severidade REVIEW, mensagem pede verificação, nunca afirma duplicidade.

## T-005 — Memória de cálculo estruturada

- **Objetivo:** cada achado com valores comparáveis mostra como foi calculado (M-07).
- **Arquivos:** `review.py`, testes, `references/data-contract.md`.
- **Mudança aditiva:** achados com `expected/actual/difference` ganham `calculation`: `{"formula": "<texto fixo>", "operands": {...strings decimais...}, "tolerance": "0.01", "rounding": "<descrição verificada do comportamento real>", "comparison": "abs(difference) > tolerance"}`. Valores `operands` vêm só de campos numéricos já validados. Adicionar ao relatório `rounding_policy` e `decimal_context` (precisão) no nível raiz.
- **Critérios de aceitação:** para cada código com valores (`EXP_PAYMENT_DIFF`, `PAY_NET_DIFF`, `PAY_PAID_DIFF`, `BUDGET_OVER`) um teste recomputa o resultado a partir de `calculation.operands` com `Decimal` e confere igualdade com `difference`; `rounding` documenta o que o código realmente faz. Fato verificado na auditoria: `money()` só aceita até 2 casas decimais, logo `quantize(CENT)` não arredonda nada (entrada já exata); soma e subtração de `Decimal` com até 2 casas são exatas. O implementador deve **confirmar por teste** (ex.: `'0.10'+'0.20'`, valores extremos) e registrar "sem arredondamento; entrada limitada a 2 casas" — qualquer modo de arredondamento citado deve ser o efetivo do contexto, não presumido; totais inalterados.
- **Riscos:** documentação divergir do comportamento → o teste acima valida.

## T-006 — Relatórios em português e inglês + Markdown

- **Objetivo:** M-08.
- **Arquivos:** `review.py` (ou novo módulo `messages.py` no mesmo diretório `scripts/`, cópia incluída no pacote), `templates/review-report.md`, testes, `docs/` onde o CLI é descrito.
- **Mudança:** `--lang {en,pt-BR}` (padrão `en`, preserva compatibilidade) e `--format {json,md}` (padrão `json`). Catálogo `código → mensagem` por idioma; **o campo `code` e demais campos de máquina nunca são traduzidos**; JSON passa a incluir `language`. Markdown determinístico, com cobertura, achados por linha, limitações e a frase "decisão do revisor pendente". Mesma regra de não sobrescrever.
- **Critérios de aceitação:** teste garante que todo `code` emitido tem mensagem nos dois idiomas (varrendo as constantes do motor); JSON `--lang en` idêntico ao atual salvo campos novos; MD gerado duas vezes é idêntico byte a byte; saída do Markdown não contém valores de entrada além dos já presentes no JSON.
- **Riscos:** tradução de termos contábeis: usar linguagem neutra, sem afirmar fraude ou irregularidade comprovada.

## T-008 — Documentação, licenças e versão (Claude)

Revisar `README*`, `INSTALL`, `SECURITY`, `CONTRIBUTING`, `LICENSE` (raiz, plugin e skill), `SOURCES.md` (atribuição à Receita Federal sem alegar vínculo); atualizar `CHANGELOG.md`, `ROADMAP.md`; subir para `0.1.1` em `review.py` e nos 2 `plugin.json`; manter PT/EN. Executa após T-002 e T-006.

## T-009 — Governança normativa (Claude)

`docs/RULE-REGISTRY.md` com o esquema obrigatório da Fase 4 e a lista das regras atuais (todas **não legais**, `validation_status: not_applicable`). Sem regra legal executável nesta versão.

## T-010 — Referências oficiais (Claude, requer rede)

Ler integralmente ADRs 001–010 e `flyway/sql` da RTC; `git pull` do clone (somente leitura do código, **sem** `mvnw`); conferir links de `SOURCES.md`; registrar data e commit lidos em `docs/SOURCES.md`.

---

## Planejamento v0.2.0 (somente infraestrutura; nenhuma regra legal liberada)

Ordem proposta, após a v0.1.1 aceita e autorização humana para iniciar:

| Marco | Item | Observação normativa |
|---|---|---|
| M1 | Esquema de regras versionadas + carregador + testes (T-009 prepara) | Infraestrutura apenas |
| M2 | Importação de Excel (`.xlsx`) para o contrato CSV | Biblioteca nova → **perguntar antes** (regra do projeto); alternativa: leitor `zipfile`+`xml` da stdlib restrito a valores, sem fórmulas/macros |
| M3 | Estornos e ajustes (lançamentos com referência ao original, sinal explícito) | Contrato de dados novo; dinheiro negativo hoje é rejeitado |
| M4 | Múltiplas moedas | Cotação **somente fornecida pelo usuário com fonte e data**; nunca buscar online; sem conversão silenciosa |
| M5 | Conciliação bancária (extrato CSV/OFX sintético) | Dados bancários reais jamais em serviços externos |
| M6 | Custos de pessoal na execução orçamentária | Hoje o orçamento exclui folha (declarado em `limitations`) |
| M7 | INSS, IRRF, FGTS, férias, 13º, horas extras: **somente** esqueleto, fontes e casos de teste | Cada regra nasce `status: draft`; nenhuma alíquota/faixa é incluída sem fonte primária e validação profissional |

Bloqueios humanos previstos: M2 (dependência), M7 (validação jurídica/contábil/trabalhista).
