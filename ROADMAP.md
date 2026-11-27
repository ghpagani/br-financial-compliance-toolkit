# Roadmap (proposed / proposto)

Dates are not commitments. Do not represent planned modules as available. / Datas não são compromissos; módulos planejados não estão disponíveis.

- **v0.1.0** — local CSV engine, expense and payroll arithmetic, budget matching, skill, tests.
- **v0.1.1 (in development / em desenvolvimento)** — traceable rejections, calculation memory, EN/PT reports and Markdown, sandbox-safe tests, reproducible ZIPs and plugin validation.
- **v0.2.0 (planned / planejada)** — infrastructure first; **no statutory rule is released without a primary source and professional validation**:
  1. versioned rule registry and loader (declarative rules, one rounding module with a per-rule mode, effective-period tests);
  2. Excel (`.xlsx`) import into the CSV contract — **blocked until a human decides on a dependency**; a standard-library reader restricted to values is the proposed alternative;
  3. reversals and adjustments (entries that reference the original, explicit sign);
  4. multiple currencies with user-supplied, dated and sourced exchange rates (never fetched online, never converted silently);
  5. bank reconciliation with synthetic statements;
  6. personnel costs in budget execution;
  7. payroll rule skeletons (INSS, IRRF, FGTS, vacation, 13th salary, overtime) as `draft` with sources and test cases only — no rates until validated by qualified professionals.
- **v0.3.x** — isolated adapter for the official consumption-tax calculator (CBS/IBS/IS) for supported scenarios only; never a substitute for payroll; tax retention modules only after legal review.
- **v0.4.x** — grant and donor policies, procurement, cost allocation, indirect costs, timesheets, evidence controls.
- **v0.5.x** — optional read-only MCP tools with typed inputs, local authentication and authorization, audit logs and least privilege. No payment tools.
- **v1.0** — private dashboard, role-based access, security review and independently validated rule packs.

**Português:** a v0.1.1 consolida rastreabilidade, memória de cálculo, relatórios em português/inglês e distribuição reproduzível. A v0.2.0 começa pela infraestrutura de regras versionadas; importação de Excel depende de decisão humana sobre dependência; multimoeda só com cotação informada pelo usuário, datada e com fonte; regras de folha (INSS, IRRF, FGTS, férias, 13º, horas extras) nascem como rascunho, sem alíquotas, até validação profissional. A calculadora oficial de CBS/IBS/IS será usada, se for, apenas por adaptador isolado e nunca para folha.
