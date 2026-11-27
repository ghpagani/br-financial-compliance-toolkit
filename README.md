# BR Financial Compliance Toolkit

[Português (Brasil)](README.pt-BR.md) | [MIT License](LICENSE) | [Security](SECURITY.md) | [Changelog](CHANGELOG.md)

An independent, local-first toolkit for financial review, internal controls and project accountability in Brazil. Inspired by the public architecture of the Brazilian Federal Revenue tax calculator; **not affiliated with the Receita Federal or any government agency**. No official certification or legal/accounting opinion.

## v0.1.1 (in development, not released) — implemented scope

- Expense review: payment discrepancies, supporting-document and approval flags, repeated vendor/invoice references and possible duplicates by vendor, amount and date.
- Payroll reconciliation: gross minus reported deductions versus reported net, net versus paid, repeated employee/competence and approval flags. No statutory calculation.
- Budget execution: cash-paid expenses matched to project/category and date windows, overspend and unmatched records; payroll not included in budget totals.
- Versioned user-provided policy, exact decimal money (no rounding is applied; input is limited to two decimal places), per-row findings with the physical file line, coverage and explicit exclusions.
- Traceability: every rejected row carries a fixed `reason` and the `field`; discrepancy findings carry a structured, recomputable `calculation` (formula, operands, tolerance).
- Local Python CLI; no network calls or third-party dependencies. Reports in English or Brazilian Portuguese (`--lang en|pt-BR`), as JSON or deterministic Markdown (`--format json|md`). Machine fields such as `code` are never translated.
- Reproducible distribution: validation of the plugin structure and byte-reproducible ZIPs with checksums (see below).

## Quick start

Python 3.10+; run from repository root. All example data is fictional. Python 3.10 reached upstream end of life in October 2026; use a currently maintained Python version when possible.

```bash
python plugins/br-financial-compliance/skills/br-financial-compliance/scripts/review.py --policy plugins/br-financial-compliance/skills/br-financial-compliance/examples/policy.json --expenses plugins/br-financial-compliance/skills/br-financial-compliance/examples/expenses.csv --payroll plugins/br-financial-compliance/skills/br-financial-compliance/examples/payroll.csv --budgets plugins/br-financial-compliance/skills/br-financial-compliance/examples/budgets.csv --out demo-report.json
python -m unittest discover -s tests -v
```

Exit codes: 0 no configured finding; 1 review findings; 2 invalid/ambiguous rows (blockers); 3 input/output failure. The sample intentionally returns 1. Output cannot overwrite an existing file. See [data contract](docs/DATA-CONTRACT.md). Store real inputs and reports outside the repository, under organization-approved access controls. Do not commit reports or personal data.

Report options: `--lang en|pt-BR` (default `en`) and `--format json|md` (default `json`). Row numbers are the physical line where each CSV record starts. The report file is written through a temporary file in the same directory and published without overwriting, which requires a **local volume that supports hard links** (for example NTFS, ext4 or APFS). On volumes without that support (FAT/exFAT, many network shares and cloud-drive mounts) the run fails with exit code 3 and writes nothing; choose another output folder. Invalid command-line options are rejected by the argument parser with exit code 2, which is not the "blocker" code of the review engine.

## Validate and build the distribution

```bash
python scripts/validate_plugin.py
python scripts/build_release.py --out-dir dist
```

The build reads only Git-tracked plugin files, normalizes line endings, fixes timestamps and permissions, writes two ZIPs (skill and plugin) and `SHA256SUMS`, and refuses to overwrite existing output. Two builds on the same machine produce identical hashes; archives built with a different zlib version may differ in bytes even when the content is identical. Building a ZIP does not publish a release: releases need explicit human authorization.

## Verification status

- Test suite: `python -m unittest discover -s tests -v` (synthetic data only). Run locally on Windows with Python 3.12.
- Python 3.10 is the declared compatibility minimum, but is no longer supported upstream. See the pull request checks for the Python versions actually tested.
- GitHub Actions is configured for Ubuntu, Windows and macOS with Python 3.10 through 3.15. Consult the pull request checks for actual results; configuration alone is not a passing run.
- Plugin marketplace manifests are experimental until installed in a real host.

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
