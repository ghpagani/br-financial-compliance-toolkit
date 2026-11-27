# BR Financial Compliance Toolkit

[English](README.md) | [Licença MIT](LICENSE) | [Segurança](SECURITY.md) | [Changelog](CHANGELOG.md)

Projeto independente de código aberto para apoiar revisão financeira, controles internos e prestação de contas no Brasil. Inspirado nas decisões arquiteturais públicas da calculadora de tributos da Receita Federal, sem vínculo institucional ou certificação oficial.

## O que a versão 0.1.1 (em desenvolvimento, não publicada) faz

| Módulo | Funcionalidade real |
|---|---|
| Despesas | Divergência entre bruto e pago, referências de fornecedor/documento repetidas, possíveis repetições por fornecedor, valor e data, documentação e aprovação declaradas |
| Pagamentos de funcionários | Conciliação de bruto, descontos informados, líquido e valor pago; alertas de repetição e aprovação |
| Orçamento | Pagamentos de despesas por projeto, categoria e período; excesso e despesas sem orçamento correspondente |
| Evidências | Código de regra, linha física do arquivo, versão da política, motivo e campo de cada rejeição, memória de cálculo recomputável (fórmula, operandos, tolerância) e cobertura |
| Relatórios | JSON ou Markdown determinístico, em português ou inglês (`--lang pt-BR\|en`, `--format json\|md`); campos de máquina como `code` nunca são traduzidos |
| Distribuição | Validação da estrutura do plugin e ZIPs reproduzíveis com somas de verificação |

Não calcula encargos legais, impostos nem folha de pagamento completa. Nenhum arredondamento é aplicado: a entrada é limitada a duas casas decimais e a aritmética é decimal exata. Não valida a autenticidade de documentos. Não executa pagamentos. Não substitui contador, auditor ou responsável financeiro.

## Executar localmente

Instale Python 3.10 ou superior. Na raiz do repositório, rode:

```powershell
python plugins/br-financial-compliance/skills/br-financial-compliance/scripts/review.py --policy plugins/br-financial-compliance/skills/br-financial-compliance/examples/policy.json --expenses plugins/br-financial-compliance/skills/br-financial-compliance/examples/expenses.csv --payroll plugins/br-financial-compliance/skills/br-financial-compliance/examples/payroll.csv --budgets plugins/br-financial-compliance/skills/br-financial-compliance/examples/budgets.csv --out demo-report.json
python -m unittest discover -s tests -v
```

O exemplo é fictício e contém divergências propositais; código de saída 1 é esperado. Consulte `demo-report.json`. Não sobrescreve arquivos. Para entradas reais, exporte planilhas para CSV UTF-8 com vírgulas e valores decimais sem separador de milhares. Leia [contrato de dados](docs/DATA-CONTRACT.md). Use arquivos locais protegidos fora do GitHub.

Opções do relatório: `--lang en|pt-BR` (padrão `en`) e `--format json|md` (padrão `json`). O número de linha é a linha física em que cada registro do CSV começa. O relatório é gravado por um arquivo temporário na mesma pasta e publicado sem sobrescrever, o que exige um **volume local com suporte a hard links** (por exemplo NTFS, ext4 ou APFS). Em volumes sem esse suporte (FAT/exFAT, muitos compartilhamentos de rede e unidades de nuvem montadas) a execução falha com código de saída 3 e não grava nada; escolha outra pasta de saída. Opções de linha de comando inválidas são recusadas pelo analisador de argumentos com código 2, que não é o código de "bloqueio" do motor de revisão.

Códigos de saída do motor: 0 sem achados configurados; 1 achados para revisão; 2 linhas inválidas ou ambíguas (bloqueios); 3 falha de entrada/saída. O exemplo retorna 1 de propósito. Um achado é um pedido de revisão, não prova de fraude; um resultado limpo significa apenas ausência de achados configurados para os dados fornecidos.

## Validar e gerar a distribuição

```powershell
python scripts/validate_plugin.py
python scripts/build_release.py --out-dir dist
```

A geração lê apenas arquivos do plugin versionados no Git, normaliza fins de linha, fixa datas e permissões, grava dois ZIPs (skill e plugin) e o `SHA256SUMS`, e não sobrescreve saídas existentes. Duas gerações na mesma máquina produzem hashes idênticos; arquivos gerados com outra versão da zlib podem diferir nos bytes mesmo com conteúdo igual. Gerar um ZIP não publica uma versão: a publicação exige autorização humana explícita.

## Situação da verificação

- Testes: `python -m unittest discover -s tests -v` (somente dados sintéticos), executados localmente no Windows com Python 3.12.
- Python 3.10 é o mínimo declarado e foi verificado apenas de forma estática (todos os arquivos do projeto são válidos na gramática do 3.10 e não há APIs posteriores da biblioteca padrão); os testes não foram executados no 3.10.
- O fluxo do GitHub Actions (Ubuntu e Windows, Python 3.10 e 3.12) está configurado, mas não foi executado para esta versão. Não o interprete como resultado aprovado.
- Os manifestos de marketplace são experimentais até a instalação real em um host.

## Instalar a skill

Copie a pasta inteira `plugins/br-financial-compliance/skills/br-financial-compliance` para `$HOME/.claude/skills/` (Claude Code) ou `$HOME/.agents/skills/` (Codex). Em ferramentas web compatíveis com upload de skills, use o ZIP individual. Caso não exista essa opção, adicione a skill e as referências como instruções de um Projeto. A instalação web não equivale a processamento local; não envie dados sigilosos sem autorização.

Consulte [guia de instalação](docs/INSTALL.md) para Windows e Orca. Invocação: `/br-financial-compliance` (Claude Code), `$br-financial-compliance` (Codex), conforme o suporte do host. Os manifestos de marketplace são experimentais até instalação real.

## Evolução

O [roadmap](ROADMAP.md) contempla legislação trabalhista/tributária, adaptador da calculadora RTC, prestação de contas avançada, MCP e dashboard. Nenhum desses módulos futuros está implementado. As regras legais deverão ser versionadas, documentadas e validadas com profissionais habilitados antes de uso operacional.

Acesse [fontes e atribuições](docs/SOURCES.md), [governança de regras](docs/RULE-GOVERNANCE.md), [segurança](SECURITY.md) e [contribuição](CONTRIBUTING.md).
