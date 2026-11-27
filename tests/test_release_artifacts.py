import json
import re
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path, PurePosixPath

from support import temporary_directory
from test_review import ROOT


class ReleaseArtifactTests(unittest.TestCase):
    def test_both_archives_are_safe_and_run_in_both_languages_and_formats(self):
        version = json.loads((ROOT / 'plugins/br-financial-compliance/plugin.json').read_text(encoding='utf-8'))['version']
        forbidden = re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9_]{30,}\b|\bAKIA[0-9A-Z]{16}\b')
        expected_totals = {'expense_paid_processed': '2850.00', 'payroll_paid_processed': '9000.00', 'expense_paid_matched_to_budget': '2650.00'}
        with temporary_directory() as directory:
            root = Path(directory)
            out = root / 'z'
            subprocess.run([sys.executable, str(ROOT / 'scripts/build_release.py'), '--out-dir', str(out)], cwd=ROOT, check=True)
            for package in ('skill', 'plugin'):
                with self.subTest(package=package):
                    archive_path = out / f'br-financial-compliance-{package}-{version}.zip'
                    extracted = root / package
                    with zipfile.ZipFile(archive_path) as archive:
                        self.assertIsNone(archive.testzip())
                        for info in archive.infolist():
                            path = PurePosixPath(info.filename)
                            self.assertFalse(path.is_absolute() or '..' in path.parts)
                            self.assertNotIn('__pycache__', path.parts)
                            self.assertNotIn('reports', path.parts)
                            self.assertNotRegex(info.filename, r'(?i)(?:\.pyc|\.pem|\.key|\.env|demo-report[^/]*)$')
                            self.assertIsNone(forbidden.search(archive.read(info)))
                        archive.extractall(extracted)
                    skill = extracted / 'br-financial-compliance'
                    if package == 'plugin':
                        skill /= 'skills/br-financial-compliance'
                    for language in ('en', 'pt-BR'):
                        for fmt in ('json', 'md'):
                            report = root / f'{package}-{language}.{fmt}'
                            args = [sys.executable, str(skill / 'scripts/review.py'), '--policy', str(skill / 'examples/policy.json'),
                                    '--lang', language, '--format', fmt, '--out', str(report)]
                            for kind in ('expenses', 'payroll', 'budgets'):
                                args.extend(['--' + kind, str(skill / f'examples/{kind}.csv')])
                            result = subprocess.run(args, capture_output=True, text=True)
                            self.assertEqual(result.returncode, 1, result.stderr)
                            text = report.read_text(encoding='utf-8')
                            if fmt == 'json':
                                data = json.loads(text)
                                self.assertEqual(data['tool_version'], version)
                                self.assertEqual(data['language'], language)
                                self.assertEqual(data['totals'], expected_totals)
                            else:
                                self.assertIn('2850.00', text)
                                self.assertIn('pendente' if language == 'pt-BR' else 'pending', text.lower())
