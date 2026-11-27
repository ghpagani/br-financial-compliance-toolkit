# Data contract (v0.1.1) / Contrato de dados

CSV UTF-8 (BOM accepted), comma-delimited, header names exactly as listed, no additional columns. Use opaque IDs beginning with a letter, followed by letters, digits, `_` or `-` (max 40 characters). Never use actual names, CPF, bank numbers or beneficiary identifiers. Pseudonymization is not necessarily anonymization. Use one organization's dataset per run. Dates ISO YYYY-MM-DD, payroll competence YYYY-MM. Amounts are non-negative strings with dot decimal, maximum 14 integer digits and two decimals (e.g. `1234.50`). BRL only. No locale inference, negative/refund records, foreign currency, or rounding of input. Flags `yes`, `no`, `unknown` are declared evidence status, not authentication.

## Expenses
`id,date,project,category,vendor,invoice,gross,paid,currency,document,approval`

One row per payment record. `date` is payment date, `gross` is the gross amount associated with that record, `paid` cash paid. Use stable opaque vendor and invoice references to detect repeated references; include series/type in the mapping if necessary. Repeated invoices can be legitimate. IDs unique within module. A missing invoice reference is unsupported; do not invent one. Convert actual data only with permission and maintain a local protected mapping if needed.

## Payroll
`id,period,employee,gross,deductions,net,paid,currency,approval`

One row per employee/run; `deductions` is reported total, not legally verified. Period is competence; the entire month must be in the policy validity window. Does not check bank statement, tax rates, statutory deadlines or legality of deductions.

## Budgets
`project,category,start,end,approved,currency`

One approved cash-payment budget per project/category/non-overlapping inclusive date interval. Expense payment date drives matching. Payroll and accruals are not included. A supplied budget does not establish authority or completeness. If no budgets are supplied, expense matching is reported as unmatched. Overlapping intervals block matching for that key.

## Policy JSON
See `examples/policy.json`. Required keys: `version` opaque identifier, `effective_from`, `effective_to` ISO dates inclusive, `currency` BRL, `tolerance` decimal string 0.00 or 0.01, `require_document`/`require_approval` Boolean, `source` nonconfidential reference to approved policy. The demo policy is fictional. Do not put sensitive text in `source` (included in report).

## Output / interpretation
`--lang en|pt-BR` selects human-readable language (default `en`); `--format json|md` selects JSON (default) or Markdown. Machine identifiers and calculation fields are not translated. Invalid command-line choices are usage errors from argparse (exit 2), distinct from the engine's exit 2 for blockers. Markdown escapes policy source and other displayed values; reviewer decision remains pending.

The report includes `rounding_policy` and `decimal_context.precision` for the calculation context. Monetary input accepts at most two decimal places; `Decimal` arithmetic in the supported scope is exact and applies no rounding. Findings with `expected`, `actual` and `difference` include `calculation`: a fixed formula and comparison, validated decimal-string operands, tolerance and rounding description. Budget excess compares actual to expected plus tolerance; the other numeric findings compare absolute difference to tolerance.

JSON with row-level findings and expected/actual/difference where relevant, policy version, totals, coverage and limitations. Monetary amounts serialized as decimal strings. Row numbers are the physical line where each CSV record starts, including when quoted fields span multiple lines. INPUT_INVALID findings include a fixed reason and, where applicable, the field name; malformed CSV headers and rows abort the run with exit code 3. Invalid rows excluded; processed totals include flagged rows. No cross-module combined total (may overlap). Report may contain confidential amounts: keep local and protected. Exit 0 no configured findings; 1 review findings; 2 blockers; 3 input/output error. Header or malformed CSV errors abort the run. Maximum 100000 rows per file. The CLI is not a security boundary for hostile files; run in a controlled environment. No network calls.

## Rejection reasons (`INPUT_INVALID`)
Each rejected row carries a `reason` from this closed set (fixed literals, never text taken from the input) and, when applicable, the `field` (a column name of the contract). Rejected rows are excluded from totals and reported as blockers (exit 2).

| `reason` | Meaning | Typical `field` |
|---|---|---|
| `DUPLICATE_ID` | `id` repeated within the module; every row with that id is excluded | `id` |
| `CURRENCY` | currency differs from the policy currency | `currency` |
| `OUT_OF_PERIOD` | date outside the policy validity window | `date`, `start`, `end`, `period` |
| `PARTIAL_COMPETENCE` | payroll competence not entirely inside the validity window | `period` |
| `INVALID_DATE` | not a calendar-valid ISO date or competence (ASCII digits only) | `date`, `period`, `start`, `end` |
| `INVALID_AMOUNT` | not a canonical non-negative decimal string (at most 14 integer digits and 2 decimals) | `gross`, `paid`, `deductions`, `net`, `approved` |
| `INVALID_REFERENCE` | not an opaque identifier | `id`, `project`, `category`, `vendor`, `invoice`, `employee` |
| `INVALID_FLAG` | not `yes`, `no` or `unknown` | `document`, `approval` |
| `INVALID_PAYROLL` | reported deductions greater than gross | `deductions` |
| `INVALID_BUDGET_DATES` | budget `start` after `end` | none |
| `MALFORMED_ROW` | defensive fallback when a required value is missing in the data given to the engine; structural CSV errors abort the run (exit 3) instead | none |

Finding codes and their conditions are listed in the rule registry of the repository.

## Contrato de dados — resumo em português
CSV UTF-8 (BOM aceito), separado por vírgulas, com os nomes de coluna exatamente como acima e sem colunas extras. Identificadores opacos começam com letra, seguida de letras, dígitos, `_` ou `-` (até 40 caracteres); nunca use nomes, CPF, dados bancários ou identificadores de beneficiários reais. Pseudonimização não é necessariamente anonimização. Use o conjunto de dados de uma única organização por execução. Datas em ISO `AAAA-MM-DD`, competência da folha `AAAA-MM`. Valores são textos não negativos com ponto decimal, até 14 dígitos inteiros e duas casas (ex.: `1234.50`). Somente BRL; não há inferência de formato regional, registros negativos/estornos, moeda estrangeira nem arredondamento de entrada. Os indicadores `yes`, `no`, `unknown` declaram o status de evidência e não autenticam documentos.

- **Despesas:** uma linha por registro de pagamento; `date` é a data do pagamento, `gross` o valor bruto associado e `paid` o valor pago em caixa. Referências repetidas de fornecedor e documento podem ser legítimas; uma referência de documento ausente não é suportada (não invente uma).
- **Folha:** uma linha por funcionário e processamento; `deductions` é o total informado, não verificado juridicamente. A competência inteira deve estar na janela de vigência da política. Não verifica extrato bancário, alíquotas, prazos legais nem a legalidade dos descontos.
- **Orçamentos:** um orçamento de pagamentos em caixa por projeto e categoria, em intervalos inclusivos que não se sobrepõem; a data de pagamento da despesa define a associação. Folha e provisões não entram. Um orçamento informado não prova autoridade nem completude. Intervalos sobrepostos bloqueiam a associação daquela chave.
- **Política (JSON):** chaves `version`, `effective_from`, `effective_to`, `currency` (BRL), `tolerance` (`0.00` ou `0.01`), `require_document`, `require_approval` e `source`. A política de exemplo é fictícia; não coloque texto sensível em `source`, pois ele aparece no relatório.
- **Saída:** `--lang en|pt-BR` e `--format json|md`. Campos de máquina (`code`, `severity`, `reason`, `field`, fórmulas e operandos) não são traduzidos. O número de linha é a linha física em que o registro começa. Achados com `expected`, `actual` e `difference` trazem `calculation` (fórmula fixa, operandos decimais validados, tolerância e descrição do arredondamento); nenhum arredondamento é aplicado. Linhas rejeitadas são excluídas dos totais; os totais processados incluem linhas sinalizadas. Códigos de saída: 0 sem achados configurados; 1 achados para revisão; 2 bloqueios; 3 erro de entrada/saída (inclui cabeçalho ou linha CSV malformados). Opções de linha de comando inválidas saem com 2 pelo `argparse`, distinto do 2 de bloqueio. Máximo de 100000 linhas por arquivo. A decisão do revisor continua pendente.

**Motivos de rejeição** (`reason`): `DUPLICATE_ID` (id repetido; todas as linhas com esse id são excluídas), `CURRENCY` (moeda diferente da política), `OUT_OF_PERIOD` (data fora da vigência), `PARTIAL_COMPETENCE` (competência da folha só parcialmente coberta), `INVALID_DATE` (data ou competência inválida; só dígitos ASCII), `INVALID_AMOUNT` (valor fora do formato canônico), `INVALID_REFERENCE` (identificador não opaco), `INVALID_FLAG` (fora de `yes`/`no`/`unknown`), `INVALID_PAYROLL` (descontos maiores que o bruto), `INVALID_BUDGET_DATES` (início após o fim) e `MALFORMED_ROW` (fallback defensivo; erros estruturais de CSV abortam a execução com código 3).
