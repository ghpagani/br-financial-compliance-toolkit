# Source register / atribuições

Architecture reviewed 2026-11-27: [Receita Federal RTC calculator](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular), [README](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/README.md), [MIT license](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/LICENSE), [ADR001](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/docs/adr/ADR001-calculo-tributario-por-expressao.md), [ADR003](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/docs/adr/ADR003-estrategia-de-precisao-numerica.md), [ADR010](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular/blob/main/docs/adr/ADR010-estrategia-de-observabilidade.md). Principles: versioned rules, precise decimal arithmetic, traceability, per-item errors and local execution. No upstream source code or tax tables copied. Upstream re-read on 2026-11-27 at commit `0d4b073` (2026-11-26, tag 1.7.3); ADR003 was rewritten upstream on 2026-11-17 (exact internal arithmetic, one rounding per published number, HALF_EVEN adopted as a project convention, not a statutory rule). The toolkit adopts none of this as a legal rule. The RTC API covers consumption taxes, not payroll.

Official reference registry for future modules (not incorporated as executable statutory rules):
- Receita Federal: https://www.gov.br/receitafederal/pt-br
- eSocial technical documentation, including rubrics and layouts: https://www.gov.br/esocial/pt-br/documentacao-tecnica/ (verified 2026-11-27)
- CLT: https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm (not reachable from the development machine on 2026-11-27: timeout; unverified)
- LGPD: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm (not reachable from the development machine on 2026-11-27: timeout; unverified)
- Previdência: https://www.gov.br/previdencia/pt-br
- Ministério do Trabalho: https://www.gov.br/trabalho-e-emprego/pt-br
- CFC: https://cfc.org.br/
- Banco Central: https://www.bcb.gov.br/
- ANPD: https://www.gov.br/anpd/pt-br

For every new legal control record exact act/article/table, effective period, retrieval date, scope, version, exceptions, reviewer and tests. Do not apply future tables retroactively. A portal URL is not sufficient legal evidence. Verify current official text and applicability before implementation. The supplied demo policy is fictional.

## Português
Registro de fontes e atribuições. A arquitetura da calculadora de tributos da Receita Federal (RTC) foi usada **somente como referência de princípios** (regras versionadas, aritmética decimal explícita, rastreabilidade, erro por item e execução local); nenhum código ou tabela foi copiado e o projeto não tem vínculo com a Receita Federal. A referência foi relida em 27/11/2026 no commit `0d4b073` (26/11/2026, tag 1.7.3); o ADR003 foi reescrito upstream em 17/11/2026 (aritmética interna exata, um arredondamento por número publicado, `HALF_EVEN` como convenção do projeto e não como regra legal).

As fontes oficiais listadas acima são um registro para módulos futuros, não regras incorporadas. Em 27/11/2026 todos os links responderam HTTP 200, exceto os dois do Planalto (CLT e LGPD), que não responderam a partir da máquina de desenvolvimento (timeout) e portanto **não foram verificados**. Um portal oficial não é evidência jurídica suficiente: cada regra legal futura exige ato, artigo ou tabela exatos, vigência, data de consulta, revisor e testes.
