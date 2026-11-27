# Changelog

## Unreleased (v0.1.1, in development / em desenvolvimento)

### Added / Adicionado
- Rejection traceability: `INPUT_INVALID` findings carry a fixed `reason` and the `field`. / Rastreabilidade das rejeições: `reason` fixo e `field` em `INPUT_INVALID`.
- Rule `EXP_POSSIBLE_DUPLICATE_AMOUNT`: same vendor, paid amount and date with different invoice references (review request only). / Regra de possível repetição por fornecedor, valor e data.
- Structured, recomputable `calculation` (formula, operands, tolerance, comparison, rounding) on discrepancy findings; `rounding_policy` and `decimal_context` at report level. / Memória de cálculo estruturada e recomputável.
- Reports in English and Brazilian Portuguese (`--lang`) and deterministic Markdown (`--format md`). / Relatórios em inglês e português e Markdown determinístico.
- `scripts/validate_plugin.py` and `scripts/build_release.py` (byte-reproducible ZIPs and `SHA256SUMS`); CI matrix for Ubuntu/Windows with Python 3.10 and 3.12 (configured, not yet run). / Validação do plugin e ZIPs reproduzíveis.
- Tests: CLI exit codes, malformed CSV, Unicode, limits, tolerance boundaries, determinism, output safety, calculation recomputation, localization. / Testes de CLI, CSV malformado, limites e determinismo.

### Changed / Alterado
- **Behavior change:** `row` is now the physical file line where the CSV record starts (it was the record index). Identical for CSV files without multiline fields. / `row` passa a ser a linha física do arquivo; antes era o índice do registro.
- The report is written through a temporary file and published without overwriting; no partial file is left on failure. It requires a volume that supports hard links; otherwise exit code 3. / Gravação por arquivo temporário; exige volume com hard link.
- Example data moved inside the skill (`plugins/br-financial-compliance/skills/br-financial-compliance/examples/`); the repository-root `examples/` directory was removed. / Exemplos movidos para dentro da skill.
- Tests no longer use the system temporary directory. / Testes não usam mais o diretório temporário do sistema.
- `review()` sets its own decimal context (precision 40). / `review()` define o próprio contexto decimal.

### Notes / Observações
- All v0.1.0 report fields, exit codes 0–3 and the demo totals are preserved; new fields are additive.
- No statutory calculation was added. Legal rules require primary sources and professional validation (see `docs/RULE-REGISTRY.md`).

## 0.1.0 — initial preview
- Local CSV review and JSON report.
- Expense checks, payroll arithmetic, budget matching.
- Portable Agent Skill, optional unverified plugin scaffolding, synthetic fixtures and tests.
- Statutory calculations, external integrations and dashboard are not implemented.
