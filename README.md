# BR Financial Compliance Toolkit

[Português (Brasil)](README.pt-BR.md) | [MIT License](LICENSE) | [Security](SECURITY.md)

An independent, local-first toolkit for financial review, internal controls and project accountability in Brazil. Inspired by the public architecture of the Brazilian Federal Revenue tax calculator; **not affiliated with the Receita Federal or any government agency**. No official certification or legal/accounting opinion.

## v0.1.0 — implemented scope

- Expense review: payment discrepancies, supporting-document and approval flags, repeated vendor/invoice references.
- Payroll reconciliation: gross minus reported deductions versus reported net, net versus paid, repeated employee/competence and approval flags. No statutory calculation.
- Budget execution: cash-paid expenses matched to project/category and date windows, overspend and unmatched records; payroll not included in budget totals.
- Versioned user-provided policy, exact decimal money, per-row findings, coverage and explicit exclusions.
- Local Python CLI; no network calls or third-party dependencies. English report messages. Agent Skill can explain results in Portuguese.

## Quick start

Python 3.10+; run from repository root. All example data is fictional.

```bash
python plugins/br-financial-compliance/skills/br-financial-compliance/scripts/review.py --policy examples/policy.json --expenses examples/expenses.csv --payroll examples/payroll.csv --budgets examples/budgets.csv --out demo-report.json
python -m unittest discover -s tests -v
```

Exit codes: 0 no configured finding; 1 review findings; 2 invalid/ambiguous rows (blockers); 3 input/output failure. The sample intentionally returns 1. Output cannot overwrite an existing file. See [data contract](docs/DATA-CONTRACT.md). Store real inputs and reports outside the repository, under organization-approved access controls. Do not commit reports or personal data.

## Agent Skill

Canonical directory: `plugins/br-financial-compliance/skills/br-financial-compliance/`. Copy the entire directory into `~/.claude/skills/` (Claude Code) or `~/.agents/skills/` (Codex), or use corresponding project-level directories. Invoke `/br-financial-compliance` or `$br-financial-compliance` respectively, where supported. For web custom skill upload, use the standalone ZIP when the workspace supports it; otherwise add SKILL.md and references to a project. A web host may process data in the cloud, unlike local CLI; never upload confidential data without authorization.

Example prompt: “Use br-financial-compliance to review the synthetic inputs locally. Report coverage, evidence, findings and limitations. Do not pay or modify anything.”

Optional plugin manifests are included as integration scaffolding, not host-verified. Claude marketplace:

```text
/plugin marketplace add ghpagani/br-financial-compliance-toolkit
/plugin install br-financial-compliance@br-financial-compliance-marketplace
```

Codex marketplace, if supported: `codex plugin marketplace add ghpagani/br-financial-compliance-toolkit`. The portable directory installation is the fallback. These commands assume the repository has been published under that exact owner/name. See [installation guide](docs/INSTALL.md).

## Financial and legal boundaries

No INSS, IRRF, FGTS, férias, 13º, rescisão or CBS/IBS/IS statutory engine is implemented. No banking/ERP connector, OCR, XLSX parser, dashboard or MCP server is shipped. CSV export is the current input method. A future RTC adapter may call the official engine only for supported consumption-tax scenarios; never substitute it for payroll. See [roadmap](ROADMAP.md), [source register](docs/SOURCES.md) and [rule governance](docs/RULE-GOVERNANCE.md).

A finding is a request for review, not proof of fraud. A clean result means only no configured finding for the supplied data. Missing data is not evidence of compliance. No automatic payments, filing, employment decisions or approval.

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Use synthetic examples only. Independently developed implementation; upstream code was studied but not copied. Architecture references are credited in docs/SOURCES.md.
