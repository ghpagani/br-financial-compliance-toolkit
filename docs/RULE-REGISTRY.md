# Registro de regras

Distinção obrigatória de **tipo**: `legal` (norma), `contratual`, `institucional` (política da organização), `simulacao` (hipótese), `aritmetica` (verificação interna sem fundamento normativo).
**Não há nenhuma regra legal executável na v0.1.x.** Todas as regras abaixo são `aritmetica` ou dependem da política fornecida pelo usuário. Tributos da Reforma Tributária do Consumo (CBS/IBS/IS) não se confundem com encargos de folha.

## Esquema obrigatório de regra executável (Fase 4)

Campos: `id`, `descricao`, `categoria`, `tipo`, `fonte_primaria_oficial`, `dispositivo_normativo`, `data_publicacao`, `vigencia_inicio`, `vigencia_fim`, `condicoes`, `excecoes`, `formula`, `arredondamento`, `versao`, `casos_de_teste`, `status_validacao` (`draft` · `em_validacao` · `validada_profissionalmente` · `obsoleta`), `historico`.
Uma regra legal só pode ser usada operacionalmente com `status_validacao = validada_profissionalmente`, registrando o revisor e a data. Antes disso é apenas rascunho.

## Regras vigentes (v0.1.0)

Versão de regra = `policy.version` informada pelo usuário. Fonte: política do usuário (a demo é fictícia). Arredondamento: nenhum (entrada com até 2 casas, aritmética decimal exata). Status: `aritmetica`, sem validação normativa aplicável.

Achados com valores comparáveis incluem memória de cálculo estruturada com fórmula fixa, operandos decimais validados, tolerância e comparação; o relatório informa a precisão do contexto decimal.

| Código | Módulo | Severidade | Condição (resumo) | Fórmula |
|---|---|---|---|---|
| `INPUT_INVALID` | todos | BLOCKER | linha inválida, fora da vigência/moeda, id duplicado, competência parcial, `deductions > gross` | — |
| `EXP_PAYMENT_DIFF` | despesas | REVIEW | `abs(gross − paid) > tolerância` | `paid − gross` |
| `EXP_DOCUMENT` | despesas | REVIEW | política exige documento e `document ≠ yes` | — |
| `EXP_APPROVAL` | despesas | REVIEW | política exige aprovação e `approval ≠ yes` | — |
| `EXP_BUDGET_UNMATCHED` | despesas | REVIEW | não há exatamente 1 orçamento aplicável (projeto, categoria, data) | — |
| `EXP_POSSIBLE_DUPLICATE` | despesas | REVIEW | repetição de `(vendor, invoice)` | — |
| `EXP_POSSIBLE_DUPLICATE_AMOUNT` | despesas | REVIEW | mesmo fornecedor, valor pago e data com referências de NF diferentes; verificar parcelas ou repetição | — |
| `PAY_NET_DIFF` | folha | REVIEW | `abs((gross − deductions) − net) > tolerância` (**não** é cálculo legal) | `net − (gross − deductions)` |
| `PAY_PAID_DIFF` | folha | REVIEW | `abs(net − paid) > tolerância` | `paid − net` |
| `PAY_APPROVAL` | folha | REVIEW | política exige aprovação e `approval ≠ yes` | — |
| `PAY_REPEAT` | folha | REVIEW | repetição de `(employee, period)` | — |
| `BUDGET_OVERLAP` | orçamento | BLOCKER | períodos sobrepostos para o mesmo projeto/categoria | — |
| `BUDGET_OVER` | orçamento | REVIEW | `pago_associado > aprovado + tolerância` (regime de caixa, só despesas fornecidas) | `pago − aprovado` |

## Regras legais

Nenhuma. Registro vazio de propósito. Primeiro candidato futuro (v0.2.0 M7): categorias de folha (INSS, IRRF, FGTS…), todas iniciando como `draft`, sem alíquotas até haver fonte primária e validação profissional.
