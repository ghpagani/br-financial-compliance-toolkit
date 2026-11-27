# Implemented controls v0.1.0

All controls are arithmetic or supplied-policy checks, not legal conclusions. REVIEW means investigate; BLOCKER means unsupported/invalid input. No configured finding is not proof of compliance.

| Code | Rule |
|---|---|
| INPUT_INVALID | Required value, reference, date, currency, ID uniqueness or schema unsupported; excludes row from processed totals |
| EXP_PAYMENT_DIFF | Gross and paid differ above tolerance; could be retention, installment, credit |
| EXP_DOCUMENT | Required supporting evidence not declared yes |
| EXP_APPROVAL / PAY_APPROVAL | Required approval not declared yes |
| EXP_POSSIBLE_DUPLICATE | Same vendor/invoice across valid rows; possible split or repeat |
| EXP_BUDGET_UNMATCHED | No unique matching budget for project/category/payment date |
| BUDGET_OVERLAP | Overlapping budget periods; matching disabled for affected project/category |
| BUDGET_OVER | Matched cash paid exceeds supplied budget beyond tolerance |
| PAY_NET_DIFF | Reported net differs from gross minus reported deductions |
| PAY_PAID_DIFF | Reported net differs from paid amount |
| PAY_REPEAT | Employee/competence repeats; may be legitimate separate payroll runs |

No configured finding verifies only these specific tests. Payroll is not included in budget totals. Incomplete data may understate expenses; flagged rows remain in processed totals. Source for arithmetic: input fields; source for approval/document requirements: supplied policy, not law.
