# Arquitetura (v0.1.0 → v0.1.1)

## Visão

Motor local, determinístico e somente leitura. Entrada: CSV (contrato em `DATA-CONTRACT.md`) + política JSON. Saída: relatório JSON (v0.1.1: também Markdown, PT/EN). Sem rede, sem banco, sem estado.

```
policy.json ─┐
expenses.csv ─┼─> read_csv/policy_load (validação estrita) ─> review() ─> relatório
payroll.csv  ─┤                                                  │
budgets.csv ─┘                              achados por linha + cobertura + totais + limitações
```

## Componentes

| Parte | Local | Responsabilidade |
|---|---|---|
| Motor/CLI | `plugins/br-financial-compliance/skills/br-financial-compliance/scripts/review.py` | validação, regras, relatório, códigos de saída 0/1/2/3 |
| Skill | `…/SKILL.md`, `references/`, `templates/` | fluxo para agentes, controles, contrato, fontes |
| Plugin | `plugins/br-financial-compliance/` | manifestos Claude Code e Codex |
| Testes | `tests/` | unidade e (v0.1.1) CLI, borda, empacotamento |
| CI | `.github/workflows/tests.yml` | testes + execução da demo |

## Invariantes

1. `Decimal` para valores; entrada canônica `^[0-9]{1,14}(\.[0-9]{1,2})?$`; sem float.
2. Linha inválida é **excluída e sinalizada**, nunca corrigida em silêncio.
3. Relatório determinístico: mesma entrada → mesmo JSON; sem horário, sem caminhos, sem eco de texto da entrada.
4. Nunca sobrescreve saída; (v0.1.1) nunca deixa arquivo parcial.
5. Totais são "processados", não certificados; cobertura e exclusões sempre declaradas.
6. Nenhum cálculo legal; regras legais só via `RULE-REGISTRY.md` com validação profissional.
7. Nenhuma rede, nenhum envio de dados.

## Evolução (v0.2.0)

Camadas planejadas, todas atrás do mesmo contrato: leitor de entrada (CSV → opcional XLSX), motor de regras versionadas (registro com vigência e status), módulos (conciliação, câmbio com cotação fornecida, estornos). Servidor MCP somente leitura apenas na v0.5 e com autenticação/autorização local (ROADMAP).
