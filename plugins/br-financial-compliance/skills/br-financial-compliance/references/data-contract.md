# Data contract (v0.1.0)

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
The report includes `rounding_policy` and `decimal_context.precision` for the calculation context. Monetary input accepts at most two decimal places; `Decimal` arithmetic in the supported scope is exact and applies no rounding. Findings with `expected`, `actual` and `difference` include `calculation`: a fixed formula and comparison, validated decimal-string operands, tolerance and rounding description. Budget excess compares actual to expected plus tolerance; the other numeric findings compare absolute difference to tolerance.

JSON with row-level findings and expected/actual/difference where relevant, policy version, totals, coverage and limitations. Monetary amounts serialized as decimal strings. Row numbers are the physical line where each CSV record starts, including when quoted fields span multiple lines. INPUT_INVALID findings include a fixed reason and, where applicable, the field name; malformed CSV headers and rows abort the run with exit code 3. Invalid rows excluded; processed totals include flagged rows. No cross-module combined total (may overlap). Report may contain confidential amounts: keep local and protected. Exit 0 no configured findings; 1 review findings; 2 blockers; 3 input/output error. Header or malformed CSV errors abort the run. Maximum 100000 rows per file. The CLI is not a security boundary for hostile files; run in a controlled environment. No network calls.
