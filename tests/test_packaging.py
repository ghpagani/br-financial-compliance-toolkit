import hashlib
import json
import shutil
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path

from support import temporary_directory
from test_review import ROOT


class PackagingTests(unittest.TestCase):
    def command(self, *args):
        return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                              capture_output=True, text=True)

    def test_validator_rejects_version_mismatch_in_copy(self):
        validator = ROOT / 'scripts/validate_plugin.py'
        result = self.command(validator)
        self.assertEqual(result.returncode, 0, result.stderr)
        with temporary_directory() as directory:
            copy = Path(directory)
            # Bytecode caches are never part of the package and lengthen paths on Windows (MAX_PATH).
            shutil.copytree(ROOT / 'plugins', copy / 'plugins', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            shutil.copytree(ROOT / '.agents', copy / '.agents')
            shutil.copytree(ROOT / '.claude-plugin', copy / '.claude-plugin')
            manifest = copy / 'plugins/br-financial-compliance/.claude-plugin/plugin.json'
            data = json.loads(manifest.read_text(encoding='utf-8'))
            data['version'] = '9.9.9'
            manifest.write_text(json.dumps(data), encoding='utf-8')
            self.assertNotEqual(self.command(validator, '--root', copy).returncode, 0)
            shutil.copyfile(ROOT / 'plugins/br-financial-compliance/.claude-plugin/plugin.json', manifest)
            result = self.command(validator, '--root', copy)
            self.assertEqual(result.returncode, 0, result.stderr)
            skill = copy / 'plugins/br-financial-compliance/skills/br-financial-compliance'
            for path, heading, error in [
                (skill / 'SKILL.md', '# BR Financial Compliance Toolkit v', 'Skill heading version'),
                (skill / 'references/controls.md', '# Implemented controls v', 'Controls heading version'),
            ]:
                with self.subTest(path=path.name):
                    original = path.read_text(encoding='utf-8')
                    import re
                    changed, count = re.subn(re.escape(heading) + r'[0-9]+\.[0-9]+\.[0-9]+', heading + '9.9.9', original, count=1)
                    self.assertEqual(count, 1)
                    path.write_text(changed, encoding='utf-8')
                    result = self.command(validator, '--root', copy)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(error, result.stderr)
                    path.write_text(original, encoding='utf-8')

    def test_build_reproducibility_contents_and_extracted_demo(self):
        builder = ROOT / 'scripts/build_release.py'
        tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', 'plugins/br-financial-compliance/'], cwd=ROOT).decode().split('\0')
        files = [Path(p) for p in tracked if p]
        plugin = Path('plugins/br-financial-compliance')
        skill = plugin / 'skills/br-financial-compliance'
        with temporary_directory() as directory:
            root = Path(directory)
            one, two = root / 'one', root / 'two'
            for out in [one, two]:
                result = self.command(builder, '--out-dir', out)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotEqual(self.command(builder, '--out-dir', one).returncode, 0)
            version = json.loads((ROOT / plugin / 'plugin.json').read_text(encoding='utf-8'))['version']
            names = [f'br-financial-compliance-skill-{version}.zip',
                     f'br-financial-compliance-plugin-{version}.zip']
            sums = (one / 'SHA256SUMS').read_text(encoding='utf-8').splitlines()
            for name, base in zip(names, [skill, plugin]):
                first, second = one / name, two / name
                digest = hashlib.sha256(first.read_bytes()).hexdigest()
                self.assertEqual(digest, hashlib.sha256(second.read_bytes()).hexdigest())
                self.assertIn(f'{digest}  {name}', sums)
                expected = sorted('br-financial-compliance/' + p.relative_to(base).as_posix()
                                  for p in files if p.is_relative_to(base))
                with zipfile.ZipFile(first) as archive:
                    self.assertEqual(archive.namelist(), expected)
                    for info in archive.infolist():
                        self.assertEqual(info.date_time, (2026, 1, 1, 0, 0, 0))
                        self.assertEqual((info.create_system, info.external_attr >> 16), (3, 0o644))
                    self.assertTrue(any('/examples/' in item for item in archive.namelist()))
                    self.assertFalse(any('__pycache__' in item or item.endswith('.pyc') or
                                         'demo-report' in item or '/reports/' in item for item in archive.namelist()))
                    if base == skill:
                        archive.extractall(root / 'extracted')
            extracted = root / 'extracted/br-financial-compliance'
            report = root / 'report.json'
            command = [extracted / 'scripts/review.py', '--policy', extracted / 'examples/policy.json']
            for kind in ('expenses', 'payroll', 'budgets'):
                command += ['--' + kind, extracted / f'examples/{kind}.csv']
            result = self.command(*command, '--out', report)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(json.loads(report.read_text(encoding='utf-8'))['totals'], {
                'expense_paid_processed': '2850.00', 'payroll_paid_processed': '9000.00',
                'expense_paid_matched_to_budget': '2650.00'})
