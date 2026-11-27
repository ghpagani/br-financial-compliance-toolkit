import contextlib
import io
import json
import unittest
from pathlib import Path

from support import temporary_directory
from test_review import ROOT, m


class CliTests(unittest.TestCase):
    def run_cli(self, directory, expense, *, budget=True, output='report.json'):
        root = Path(directory)
        expense_path = root / 'expenses.csv'
        expense_path.write_text(
            'id,date,project,category,vendor,invoice,gross,paid,currency,document,approval\n'
            + expense + '\n', encoding='utf-8')
        args = ['--policy', str(ROOT / 'examples/policy.json'),
                '--expenses', str(expense_path), '--out', str(root / output)]
        if budget:
            budget_path = root / 'budgets.csv'
            budget_path.write_text('project,category,start,end,approved,currency\n'
                                   'P,C,2026-01-01,2026-12-31,100.00,BRL\n', encoding='utf-8')
            args += ['--budgets', str(budget_path)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = m.main(args)
        return code, root / output

    def test_exit_codes_and_report_presence(self):
        cases = [
            ('E,2026-06-01,P,C,V,I,10.00,10.00,BRL,yes,yes', 0, None),
            ('E,2026-06-01,P,C,V,I,10.00,9.00,BRL,yes,yes', 1, 'EXP_PAYMENT_DIFF'),
            ('E,2026-06-01,P,C,V,I,10.00,10.00,USD,yes,yes', 2, 'INPUT_INVALID'),
        ]
        for expense, expected, finding in cases:
            with self.subTest(exit_code=expected), temporary_directory() as directory:
                code, path = self.run_cli(directory, expense)
                self.assertEqual(code, expected)
                report = json.loads(path.read_text(encoding='utf-8'))
                codes = [f['code'] for f in report['findings']]
                if finding:
                    self.assertIn(finding, codes)
                else:
                    self.assertEqual(codes, [])
        with temporary_directory() as directory:
            code, path = self.run_cli(directory, 'malformed')
            self.assertEqual(code, 3)
            self.assertFalse(path.exists())

    def test_output_is_byte_deterministic(self):
        expense = 'E,2026-06-01,P,C,V,I,10.00,9.00,BRL,yes,yes'
        with temporary_directory() as directory:
            first_code, first = self.run_cli(directory, expense, output='first.json')
            second_code, second = self.run_cli(directory, expense, output='second.json')
            self.assertEqual((first_code, second_code), (1, 1))
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_invalid_input_is_not_echoed(self):
        marker = 'INJECTED_PRIVATE_TEXT!'
        with temporary_directory() as directory:
            code, path = self.run_cli(directory,
                f'E,2026-06-01,{marker},C,V,I,10.00,10.00,BRL,yes,yes')
            self.assertEqual(code, 2)
            raw = path.read_text(encoding='utf-8')
            self.assertNotIn(marker, raw)
            findings = json.loads(raw)['findings']
            self.assertTrue(any((f['code'], f['severity'], f['row']) ==
                                ('INPUT_INVALID', 'BLOCKER', 2) for f in findings))
