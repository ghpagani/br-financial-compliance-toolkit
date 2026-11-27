import contextlib
import io
import json
import unittest
from decimal import localcontext
from pathlib import Path
from unittest.mock import patch

from support import temporary_directory
from test_review import ROOT, m


class HardeningTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples'
        self.base = base
        self.policy = m.policy_load(base / 'policy.json')
        self.expense = m.read_csv(base / 'expenses.csv', 'expenses')[0]
        self.payroll = m.read_csv(base / 'payroll.csv', 'payroll')[0]
        self.budget = m.read_csv(base / 'budgets.csv', 'budgets')[0]

    def test_invalid_reason_and_field(self):
        cases = [
            ('expenses', {'id': 'bad!'}, 'INVALID_REFERENCE', 'id'),
            ('expenses', {'date': '2026-02-30'}, 'INVALID_DATE', 'date'),
            ('expenses', {'currency': 'USD'}, 'CURRENCY', 'currency'),
            ('expenses', {'date': '2025-12-31'}, 'OUT_OF_PERIOD', 'date'),
            ('expenses', {'paid': 'bad!'}, 'INVALID_AMOUNT', 'paid'),
            ('expenses', {'approval': 'bad!'}, 'INVALID_FLAG', 'approval'),
            ('payroll', {'deductions': '9999'}, 'INVALID_PAYROLL', 'deductions'),
            ('budgets', {'start': '2026-12-31', 'end': '2026-01-01'}, 'INVALID_BUDGET_DATES', None),
        ]
        for kind, changes, reason, field in cases:
            with self.subTest(reason=reason):
                data = {'expenses': [], 'payroll': [], 'budgets': []}
                data[kind] = [dict(getattr(self, {'expenses': 'expense', 'payroll': 'payroll', 'budgets': 'budget'}[kind]), **changes)]
                finding = next(f for f in m.review(**data, policy=self.policy)['findings'] if f['code'] == 'INPUT_INVALID')
                self.assertEqual((finding['reason'], finding.get('field')), (reason, field))
                self.assertNotIn('bad!', json.dumps(finding))
        duplicate = [dict(self.expense), dict(self.expense)]
        findings = m.review(duplicate, [], [], self.policy)['findings']
        self.assertEqual([f['reason'] for f in findings if f['code'] == 'INPUT_INVALID'], ['DUPLICATE_ID'] * 2)
        policy = dict(self.policy, effective_to='2026-11-15')
        finding = m.review([], [self.payroll], [], policy)['findings'][0]
        self.assertEqual((finding['reason'], finding['field']), ('PARTIAL_COMPETENCE', 'period'))
        malformed = dict(self.expense); del malformed['project']
        finding = m.review([malformed], [], [], self.policy)['findings'][0]
        self.assertEqual(finding['reason'], 'MALFORMED_ROW')

    def test_unicode_dates_are_invalid_and_not_echoed(self):
        for kind, row, key, value in [('expenses', self.expense, 'date', '٢٠٢٦-11-03'),
                                      ('payroll', self.payroll, 'period', '٢٠٢٦-11')]:
            with self.subTest(kind=kind):
                data = {'expenses': [], 'payroll': [], 'budgets': []}
                data[kind] = [dict(row, **{key: value})]
                result = m.review(**data, policy=self.policy)
                finding = next(f for f in result['findings'] if f['code'] == 'INPUT_INVALID')
                self.assertEqual((finding['reason'], finding['field']), ('INVALID_DATE', key))
                self.assertNotIn(value, json.dumps(result, ensure_ascii=False))

    def test_rejection_does_not_echo_input_in_report(self):
        marker = 'PRIVATE!SYNTHETIC!MARKER'
        result = m.review([dict(self.expense, project=marker)], [], [], self.policy)
        finding = next(f for f in result['findings'] if f['code'] == 'INPUT_INVALID')
        self.assertEqual((finding['reason'], finding['field']), ('INVALID_REFERENCE', 'project'))
        self.assertNotIn(marker, json.dumps(result, ensure_ascii=False))

    def test_physical_line_after_blank_and_multiline_records(self):
        header = 'id,date,project,category,vendor,invoice,gross,paid,currency,document,approval\n'
        rows = '\nE,2026-06-01,"P\nQ",C,V,I,10,10,BRL,yes,yes\n\nF,2026-06-01,,C,V,J,10,10,BRL,yes,yes\n'
        with temporary_directory() as directory:
            path = Path(directory) / 'input.csv'
            path.write_bytes((header + rows).encode('utf-8'))
            result = m.review(m.read_csv(path, 'expenses'), [], [], self.policy)
            self.assertEqual([f['row'] for f in result['findings'] if f['code'] == 'INPUT_INVALID'], [3, 6])

    def test_near_duplicate_requires_distinct_invoice_and_same_day_and_amount(self):
        first = dict(self.expense)
        for changes, expected in [({'id': 'E2', 'invoice': 'NF99'}, True),
                                  ({'id': 'E2'}, False),
                                  ({'id': 'E2', 'invoice': 'NF99', 'date': '2026-11-04'}, False),
                                  ({'id': 'E2', 'invoice': 'NF99', 'paid': '999.00'}, False)]:
            with self.subTest(changes=changes):
                findings = m.review([first, dict(first, **changes)], [], [], self.policy)['findings']
                near = [(f['row'], f['severity']) for f in findings if f['code'] == 'EXP_POSSIBLE_DUPLICATE_AMOUNT']
                self.assertEqual(near, [(2, 'REVIEW'), (3, 'REVIEW')] if expected else [])
                if changes == {'id': 'E2'}:
                    self.assertEqual(sum(f['code'] == 'EXP_POSSIBLE_DUPLICATE' for f in findings), 2)

    def test_output_failures_leave_no_partial_or_temporary_file(self):
        for target in ['json.dump', 'os.link']:
            with self.subTest(target=target), temporary_directory() as directory:
                out = Path(directory) / 'report.json'
                args = ['--policy', str(self.base / 'policy.json'), '--expenses', str(self.base / 'expenses.csv'), '--out', str(out)]
                with patch.object(m.json if target == 'json.dump' else m.os,
                                  'dump' if target == 'json.dump' else 'link', side_effect=OSError), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(m.main(args), 3)
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_existing_output_is_preserved_without_temp(self):
        with temporary_directory() as directory:
            out = Path(directory) / 'report.json'; out.write_text('original')
            args = ['--policy', str(self.base / 'policy.json'), '--expenses', str(self.base / 'expenses.csv'), '--out', str(out)]
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(m.main(args), 3)
            self.assertEqual(out.read_text(), 'original')
            self.assertEqual(list(Path(directory).iterdir()), [out])

    def test_review_uses_own_decimal_context(self):
        with localcontext() as context:
            context.prec = 4
            result = m.review([self.expense], [], [self.budget], self.policy)
        self.assertEqual(result['totals']['expense_paid_processed'], '1000.00')

    def test_paid_greater_than_gross_is_flagged(self):
        result = m.review([dict(self.expense, paid='1000.02')], [], [self.budget], self.policy)
        self.assertTrue(any(f['code'] == 'EXP_PAYMENT_DIFF' and f['row'] == 2 for f in result['findings']))
