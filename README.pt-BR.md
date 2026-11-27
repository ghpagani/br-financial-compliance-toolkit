# BR Financial Compliance Toolkit

[English](README.md) | [Licença MIT](LICENSE)

Projeto independente de código aberto para apoiar revisão financeira, controles internos e prestação de contas no Brasil. Inspirado nas decisões arquiteturais públicas da calculadora de tributos da Receita Federal, sem vínculo institucional ou certificação oficial.

## O que a versão 0.1.0 faz

| Módulo | Funcionalidade real |
|---|---|
| Despesas | Divergência entre bruto e pago, referências de fornecedor/documento repetidas, documentação e aprovação declaradas |
| Pagamentos de funcionários | Conciliação de bruto, descontos informados, líquido e valor pago; alertas de repetição e aprovação |
| Orçamento | Pagamentos de despesas por projeto, categoria e período; excesso e despesas sem orçamento correspondente |
| Evidências | Código de regra, linha, versão da política, valores quando aplicáveis e cobertura |

Não calcula encargos legais, impostos nem folha de pagamento completa. Não valida a autenticidade de documentos. Não executa pagamentos. Não substitui contador, auditor ou responsável financeiro.

## Executar localmente

Instale Python 3.10 ou superior. Na raiz do repositório, rode:

```powershell
python plugins/br-financial-compliance/skills/br-financial-compliance/scripts/review.py --policy plugins/br-financial-compliance/skills/br-financial-compliance/examples/policy.json --expenses plugins/br-financial-compliance/skills/br-financial-compliance/examples/expenses.csv --payroll plugins/br-financial-compliance/skills/br-financial-compliance/examples/payroll.csv --budgets plugins/br-financial-compliance/skills/br-financial-compliance/examples/budgets.csv --out demo-report.json
python -m unittest discover -s tests -v
```

O exemplo é fictício e contém divergências propositais; código de saída 1 é esperado. Consulte `demo-report.json`. Não sobrescreve arquivos. Para entradas reais, exporte planilhas para CSV UTF-8 com vírgulas e valores decimais sem separador de milhares. Leia [contrato de dados](docs/DATA-CONTRACT.md). Use arquivos locais protegidos fora do GitHub.

## Instalar a skill

Copie a pasta inteira `plugins/br-financial-compliance/skills/br-financial-compliance` para `$HOME/.claude/skills/` (Claude Code) ou `$HOME/.agents/skills/` (Codex). Em ferramentas web compatíveis com upload de skills, use o ZIP individual. Caso não exista essa opção, adicione a skill e as referências como instruções de um Projeto. A instalação web não equivale a processamento local; não envie dados sigilosos sem autorização.

Consulte [guia de instalação](docs/INSTALL.md) para Windows e Orca. Invocação: `/br-financial-compliance` (Claude Code), `$br-financial-compliance` (Codex), conforme o suporte do host. Os manifestos de marketplace são experimentais até instalação real.

## Evolução

O [roadmap](ROADMAP.md) contempla legislação trabalhista/tributária, adaptador da calculadora RTC, prestação de contas avançada, MCP e dashboard. Nenhum desses módulos futuros está implementado. As regras legais deverão ser versionadas, documentadas e validadas com profissionais habilitados antes de uso operacional.

Acesse [fontes e atribuições](docs/SOURCES.md), [governança de regras](docs/RULE-GOVERNANCE.md), [segurança](SECURITY.md) e [contribuição](CONTRIBUTING.md).
