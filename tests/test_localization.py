import contextlib
import io
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from support import temporary_directory
from test_review import ROOT, m


class LocalizationTests(unittest.TestCase):
    def setUp(self):
        self.base = ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples'

    def run_report(self, directory, language, fmt, name, policy=None):
        out = Path(directory) / name
        args = ['--policy', str(policy or self.base / 'policy.json'), '--out', str(out),
                '--lang', language, '--format', fmt]
        for kind in ('expenses', 'payroll', 'budgets'):
            args += ['--' + kind, str(self.base / f'{kind}.csv')]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = m.main(args)
        return code, out

    def test_catalog_matches_rule_registry_and_uses_neutral_terms(self):
        registry = (ROOT / 'docs/RULE-REGISTRY.md').read_text(encoding='utf-8')
        table = registry.split('## Regras vigentes', 1)[1].split('## Regras legais', 1)[0]
        codes = set(re.findall(r'^\| `([A-Z_]+)` \|', table, re.MULTILINE))
        banned = re.compile(r'fraud|fraude|irregular|ilegal|crime|culpa|desvio|m[aá]-f[eé]|roubo', re.IGNORECASE)
        for language in ('en', 'pt-BR'):
            messages = m.MESSAGES[language]['findings']
            self.assertEqual(set(messages), codes)
            for code, message in messages.items():
                with self.subTest(language=language, code=code):
                    self.assertIsNone(banned.search(message))

    def test_four_formats_and_deterministic_markdown(self):
        with temporary_directory() as directory:
            for language in ('en', 'pt-BR'):
                with self.subTest(language=language):
                    code, path = self.run_report(directory, language, 'json', language + '.json')
                    self.assertEqual(code, 1)
                    report = json.loads(path.read_text(encoding='utf-8'))
                    self.assertEqual(report['language'], language)
                    self.assertEqual(report['totals']['expense_paid_processed'], '2850.00')
                    self.assertEqual(report['findings'][0]['message'], m.MESSAGES[language]['findings'][report['findings'][0]['code']])
                    first_code, first = self.run_report(directory, language, 'md', language + '-1.md')
                    second_code, second = self.run_report(directory, language, 'md', language + '-2.md')
                    self.assertEqual((first_code, second_code), (1, 1))
                    self.assertEqual(first.read_bytes(), second.read_bytes())
                    text = first.read_text(encoding='utf-8')
                    self.assertIn('2850.00', text)
                    self.assertIn('EXP_PAYMENT_DIFF', text)
                    self.assertIn('pendente' if language == 'pt-BR' else 'pending', text.lower())

    def test_hostile_policy_source_is_safe_in_markdown(self):
        source = '|\n<script>[x](javascript:alert(1)) `code` &'
        with temporary_directory() as directory:
            path = Path(directory) / 'policy.json'
            policy = json.loads((self.base / 'policy.json').read_text(encoding='utf-8'))
            policy['source'] = source
            path.write_text(json.dumps(policy), encoding='utf-8')
            code, report = self.run_report(directory, 'pt-BR', 'md', 'report.md', path)
            self.assertEqual(code, 1)
            text = report.read_text(encoding='utf-8')
            self.assertNotIn('<script>', text)
            self.assertNotIn('[x](javascript:', text)
            self.assertNotIn('`code`', text)
            self.assertIn('&lt;script&gt;', text)
            table = [line for line in text.splitlines() if line.startswith('|')]
            self.assertTrue(table)
            for index, line in enumerate(table):
                if index and line.count('|') != table[index - 1].count('|'):
                    # A new Markdown table has its own separator in the following line.
                    self.assertTrue(index + 1 < len(table) and '---' in table[index + 1])

    def test_invalid_cli_options_are_usage_error(self):
        for option in ('--lang', '--format'):
            with self.subTest(option=option), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                m.main(['--policy', 'unused', '--out', 'unused', option, 'invalid'])
            self.assertEqual(error.exception.code, 2)

    def test_language_preserves_machine_fields_and_safe_md_write(self):
        with temporary_directory() as directory:
            reports = []
            for lang in ('en', 'pt-BR'):
                code, path = self.run_report(directory, lang, 'json', lang + '.json')
                self.assertEqual(code, 1)
                reports.append(json.loads(path.read_text(encoding='utf-8')))
            for left, right in zip(reports[0]['findings'], reports[1]['findings']):
                for key in ('module', 'row', 'code', 'severity', 'reason', 'field', 'expected', 'actual', 'difference'):
                    self.assertEqual(left.get(key), right.get(key))
                if 'calculation' in left:
                    for key in ('formula', 'operands', 'comparison', 'tolerance'):
                        self.assertEqual(left['calculation'][key], right['calculation'][key])
            self.assertEqual(reports[0]['coverage'], reports[1]['coverage'])
            self.assertEqual(reports[0]['totals'], reports[1]['totals'])
            before = set(Path(directory).iterdir())
            with patch.object(m.os, 'link', side_effect=OSError):
                code, path = self.run_report(directory, 'pt-BR', 'md', 'failed.md')
            self.assertEqual(code, 3)
            self.assertFalse(path.exists())
            self.assertEqual(set(Path(directory).iterdir()), before)
