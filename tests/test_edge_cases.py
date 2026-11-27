import json
import unittest
from pathlib import Path

from support import temporary_directory
from test_review import ROOT, m


class EdgeCaseTests(unittest.TestCase):
    def setUp(self):
        self.policy = m.policy_load(ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples/policy.json')
        self.expense = m.read_csv(ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples/expenses.csv', 'expenses')[0]
        self.payroll = m.read_csv(ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples/payroll.csv', 'payroll')[0]
        self.budget = m.read_csv(ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples/budgets.csv', 'budgets')[0]

    def test_money_boundaries(self):
        for value, expected in [('0', '0.00'), ('0.00', '0.00'),
                                ('99999999999999.99', '99999999999999.99')]:
            with self.subTest(value=value):
                self.assertEqual(str(m.money(value)), expected)
        for value in ['100000000000000.00', '.5', '5.', '+1', ' 1', '1 ', '١٢.٣٤']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                m.money(value)

    def test_invalid_dates_and_policy_boundaries(self):
        for value in ['2026-02-29', '2026-02-30', '2026-13-01']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                m.iso(value)
        for value in ['2026-01-01', '2026-12-31']:
            with self.subTest(value=value):
                self.expense['date'] = value
                result = m.review([self.expense], [], [], self.policy)
                self.assertEqual(result['coverage']['expense_processed'], 1)
        self.policy['effective_to'] = '2026-11-15'
        result = m.review([], [self.payroll], [], self.policy)
        self.assertEqual(result['coverage']['payroll_processed'], 0)
        self.assertTrue(any((f['code'], f['severity'], f['row']) ==
                            ('INPUT_INVALID', 'BLOCKER', 2) for f in result['findings']))

    def test_tolerance_expenses_and_payroll(self):
        for paid, flagged in [('1000.00', False), ('999.99', False), ('999.98', True), ('1000.02', True)]:
            with self.subTest(module='expenses', paid=paid):
                self.expense['paid'] = paid
                result = m.review([self.expense], [], [self.budget], self.policy)
                findings = [(f['code'], f['severity'], f['row']) for f in result['findings']]
                self.assertEqual(('EXP_PAYMENT_DIFF', 'REVIEW', 2) in findings, flagged)
        for net, flagged in [('4200.00', False), ('4199.99', False), ('4199.98', True)]:
            with self.subTest(module='payroll_net', net=net):
                self.payroll['net'] = net
                self.payroll['paid'] = net
                result = m.review([], [self.payroll], [], self.policy)
                findings = [(f['code'], f['severity'], f['row']) for f in result['findings']]
                self.assertEqual(('PAY_NET_DIFF', 'REVIEW', 2) in findings, flagged)
        self.payroll['net'] = '4200.00'
        for paid, flagged in [('4200.00', False), ('4199.99', False), ('4199.98', True)]:
            with self.subTest(module='payroll_paid', paid=paid):
                self.payroll['paid'] = paid
                result = m.review([], [self.payroll], [], self.policy)
                findings = [(f['code'], f['severity'], f['row']) for f in result['findings']]
                self.assertEqual(('PAY_PAID_DIFF', 'REVIEW', 2) in findings, flagged)

    def test_policy_rejects_invalid_contract(self):
        policies = []
        extra = dict(self.policy, extra=True); policies.append(extra)
        missing = dict(self.policy); del missing['source']; policies.append(missing)
        for changes in [{'tolerance': '0.02'}, {'currency': 'USD'},
                        {'effective_from': '2026-12-31', 'effective_to': '2026-01-01'}]:
            policies.append(dict(self.policy, **changes))
        with temporary_directory() as directory:
            path = Path(directory) / 'policy.json'
            for policy in policies:
                with self.subTest(policy=policy):
                    path.write_text(json.dumps(policy), encoding='utf-8')
                    with self.assertRaises(ValueError):
                        m.policy_load(path)

    def test_csv_headers_and_malformed_rows(self):
        header = 'id,date,project,category,vendor,invoice,gross,paid,currency,document,approval'
        valid = 'E,2026-06-01,P,C,V,I,10.00,10.00,BRL,yes,yes'
        cases = [header + ',id\n' + valid + ',E\n',
                 header.replace(',approval', '') + '\n' + valid + '\n',
                 header + ',extra\n' + valid + ',x\n',
                 header + '\n' + valid + ',extra\n',
                 header + '\n' + valid.rsplit(',', 1)[0] + '\n', '']
        with temporary_directory() as directory:
            path = Path(directory) / 'input.csv'
            for index, content in enumerate(cases):
                with self.subTest(case=index):
                    path.write_text(content, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        m.read_csv(path, 'expenses')

    def test_csv_bom_crlf_empty_field_header_only_and_multiline(self):
        header = 'id,date,project,category,vendor,invoice,gross,paid,currency,document,approval'
        with temporary_directory() as directory:
            path = Path(directory) / 'input.csv'
            path.write_bytes(('\ufeff' + header + '\r\nE,2026-06-01,P,C,V,I,10,10,BRL,yes,yes\r\n').encode('utf-8'))
            self.assertEqual(len(m.read_csv(path, 'expenses')), 1)
            path.write_text(header + '\n', encoding='utf-8')
            self.assertEqual(m.read_csv(path, 'expenses'), [])
            path.write_text(header + '\nE,2026-06-01,,C,V,I,10,10,BRL,yes,yes\n', encoding='utf-8')
            result = m.review(m.read_csv(path, 'expenses'), [], [], self.policy)
            self.assertTrue(any((f['code'], f['severity'], f['row']) ==
                                ('INPUT_INVALID', 'BLOCKER', 2) for f in result['findings']))
            path.write_bytes((header + '\nE,2026-06-01,"P\nQ",C,V,I,10,10,BRL,yes,yes\n').encode('utf-8'))
            rows = m.read_csv(path, 'expenses')
            self.assertEqual(rows[0]['project'], 'P\nQ')
            result = m.review(rows, [], [], self.policy)
            self.assertTrue(any((f['code'], f['severity'], f['row']) ==
                                ('INPUT_INVALID', 'BLOCKER', 2) for f in result['findings']))

    def test_csv_finding_uses_physical_line_after_multiline_record(self):
        header = 'id,date,project,category,vendor,invoice,gross,paid,currency,document,approval\n'
        first = 'E,2026-06-01,"P\nQ",C,V,I,10,10,BRL,yes,yes\n'
        second = 'F,2026-06-01,,C,V,J,10,10,BRL,yes,yes\n'
        with temporary_directory() as directory:
            path = Path(directory) / 'input.csv'
            path.write_bytes((header + first + second).encode('utf-8'))
            result = m.review(m.read_csv(path, 'expenses'), [], [], self.policy)
            invalid_rows = [f['row'] for f in result['findings'] if f['code'] == 'INPUT_INVALID']
            self.assertIn(4, invalid_rows)

    def test_csv_row_limit(self):
        header = 'id,date,project,category,vendor,invoice,gross,paid,currency,document,approval\n'
        row = 'E,2026-06-01,P,C,V,I,10,10,BRL,yes,yes\n'
        with temporary_directory() as directory:
            path = Path(directory) / 'large.csv'
            path.write_text(header + row * 100000, encoding='utf-8')
            self.assertEqual(len(m.read_csv(path, 'expenses')), 100000)
            with path.open('a', encoding='utf-8') as file:
                file.write(row)
            with self.assertRaises(ValueError):
                m.read_csv(path, 'expenses')
