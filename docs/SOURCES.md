# Source register / atribuições

Architecture reviewed 2026-11-27: [Receita Federal RTC calculator](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular), [README](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/README.md), [MIT license](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/LICENSE), [ADR001](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/docs/adr/ADR001-calculo-tributario-por-expressao.md), [ADR003](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/docs/adr/ADR003-estrategia-de-precisao-numerica.md), [ADR010](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/docs/adr/ADR010-estrategia-de-observabilidade.md). Principles: versioned rules, precise decimal arithmetic, traceability, per-item errors and local execution. No upstream source code or tax tables copied. The RTC API covers consumption taxes, not payroll.

Official reference registry for future modules (not incorporated as executable statutory rules):
- Receita Federal: https://www.gov.br/receitafederal/pt-br
- eSocial technical documentation, including rubrics and layouts: https://www.gov.br/esocial/pt-br/documentacao-tecnica/ (verified 2026-11-27)
- CLT: https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm
- LGPD: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm (verified 2026-11-27)
- Previdência: https://www.gov.br/previdencia/pt-br
- Ministério do Trabalho: https://www.gov.br/trabalho-e-emprego/pt-br
- CFC: https://cfc.org.br/
- Banco Central: https://www.bcb.gov.br/
- ANPD: https://www.gov.br/anpd/pt-br

For every new legal control record exact act/article/table, effective period, retrieval date, scope, version, exceptions, reviewer and tests. Do not apply future tables retroactively. A portal URL is not sufficient legal evidence. Verify current official text and applicability before implementation. The supplied demo policy is fictional.
