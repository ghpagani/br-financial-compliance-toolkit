import unittest
from decimal import Decimal, localcontext

from test_review import ROOT, m


class CalculationTests(unittest.TestCase):
    def test_findings_recompute_from_decimal_operands(self):
        base = ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples'
        policy = m.policy_load(base / 'policy.json')
        expenses = m.read_csv(base / 'expenses.csv', 'expenses')
        payroll = m.read_csv(base / 'payroll.csv', 'payroll')
        budgets = m.read_csv(base / 'budgets.csv', 'budgets')
        report = m.review(expenses, payroll, budgets, policy)
        self.assertEqual(report['decimal_context'], {'precision': 40})
        self.assertIn('no rounding', report['rounding_policy'].lower())
        expected_fields = {
            'EXP_PAYMENT_DIFF': {'gross', 'paid'},
            'PAY_NET_DIFF': {'gross', 'deductions', 'net'},
            'PAY_PAID_DIFF': {'net', 'paid'},
            'BUDGET_OVER': {'approved', 'matched_paid'},
        }
        formulas = {
            'EXP_PAYMENT_DIFF': 'difference = paid - gross',
            'PAY_NET_DIFF': 'difference = net - (gross - deductions)',
            'PAY_PAID_DIFF': 'difference = paid - net',
            'BUDGET_OVER': 'difference = matched_paid - approved',
        }
        seen = set()
        for finding in report['findings']:
            code = finding['code']
            if code not in expected_fields:
                self.assertNotIn('calculation', finding)
                continue
            seen.add(code)
            calc = finding['calculation']
            self.assertEqual(calc['formula'], formulas[code])
            self.assertEqual(set(calc['operands']), expected_fields[code])
            self.assertTrue(all(isinstance(value, str) for value in calc['operands'].values()))
            values = {key: Decimal(value) for key, value in calc['operands'].items()}
            tolerance = Decimal(calc['tolerance'])
            self.assertEqual(tolerance, Decimal(policy['tolerance']))
            self.assertIn('no rounding', calc['rounding'].lower())
            if code == 'EXP_PAYMENT_DIFF':
                difference = values['paid'] - values['gross']
            elif code == 'PAY_NET_DIFF':
                difference = values['net'] - (values['gross'] - values['deductions'])
            elif code == 'PAY_PAID_DIFF':
                difference = values['paid'] - values['net']
            else:
                difference = values['matched_paid'] - values['approved']
            self.assertEqual(difference, Decimal(finding['difference']))
            if code == 'BUDGET_OVER':
                self.assertEqual(calc['comparison'], 'matched_paid > approved + tolerance')
                self.assertGreater(values['matched_paid'], values['approved'] + tolerance)
            else:
                self.assertEqual(calc['comparison'], 'abs(difference) > tolerance')
                self.assertGreater(abs(difference), tolerance)
        self.assertEqual(seen, set(expected_fields))

    def test_decimal_identity_and_exact_arithmetic(self):
        with localcontext() as context:
            context.prec = 40
            for value in ['0', '0.1', '0.10', '1.01', '12.34', '99999999999999.99']:
                with self.subTest(value=value):
                    self.assertEqual(m.money(value), Decimal(value))
            self.assertEqual(Decimal('0.10') + Decimal('0.20'), Decimal('0.30'))
            self.assertEqual(Decimal('99999999999999.99') + Decimal('0.01'), Decimal('100000000000000.00'))
            self.assertEqual(Decimal('99999999999999.99') - Decimal('0.01'), Decimal('99999999999999.98'))

    def test_rejected_raw_values_never_enter_calculation(self):
        base = ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples'
        policy = m.policy_load(base / 'policy.json')
        expense = m.read_csv(base / 'expenses.csv', 'expenses')[0]
        expense['paid'] = 'PRIVATE!MARKER'
        report = m.review([expense], [], [], policy)
        self.assertNotIn('calculation', report['findings'][0])
        self.assertNotIn('PRIVATE!MARKER', str(report))
