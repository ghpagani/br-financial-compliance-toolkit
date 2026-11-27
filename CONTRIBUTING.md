# Contributing / Contribuindo

Open an issue with a synthetic, reproducible example and the expected behavior. Use synthetic data only: never include actual financial data, credentials, personal identifiers or copyrighted third-party material.

Before proposing a change run:

```bash
python -m unittest discover -s tests -v
python scripts/validate_plugin.py
```

Rules for changes:
- Monetary values are decimal strings and `Decimal`; no binary floating point, no `eval` or arbitrary expressions.
- Report fields are additive; do not change a calculation only to make a test pass. A behavior change needs a test that describes it and a line in `CHANGELOG.md`.
- A new financial rule needs source, effective period, applicability, version, calculation method, rounding procedure, edge cases and tests; a statutory rule also needs evidence of professional review and is registered in `docs/RULE-REGISTRY.md` (see `docs/RULE-GOVERNANCE.md`). Do not invent rates or legal references.
- Keep the English and Portuguese documentation accurate and in step.
- Do not state that something passes, builds or is verified unless you ran it; report what could not be verified.

Contributions are licensed under the MIT License.

**Português:** abra uma issue com exemplo sintético reproduzível e o comportamento esperado; use somente dados sintéticos. Antes de propor mudanças rode `python -m unittest discover -s tests -v` e `python scripts/validate_plugin.py`. Valores monetários são `Decimal`/texto decimal, sem float e sem `eval`. Campos de relatório são aditivos; não altere um cálculo apenas para um teste passar, e registre mudanças de comportamento no `CHANGELOG.md` com teste. Regra financeira nova exige fonte, vigência, aplicabilidade, versão, método de cálculo, critério de arredondamento, casos de borda e testes; regra legal exige também validação profissional e registro em `docs/RULE-REGISTRY.md`. Mantenha a documentação em português e inglês coerente e só afirme o que foi executado.
