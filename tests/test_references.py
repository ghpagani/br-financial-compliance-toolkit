import re
import subprocess
import unittest
from pathlib import Path

from test_review import ROOT


class ReferenceTests(unittest.TestCase):
    def test_tracked_documents_example_files_exist(self):
        # Skill documents use skill-relative paths; other documents use repository-relative paths.
        # Only concrete CSV/JSON paths are references; directory mentions and globs are not.
        skill = ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance'
        pattern = re.compile(r'(?<![\w./-])((?:[\w.-]+/)*examples/[\w.-]+\.(?:csv|json))')
        tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', '*.md', '*.json'], cwd=ROOT)
        missing = []
        for name in tracked.decode('utf-8').split('\0'):
            if not name:
                continue
            source = ROOT / name
            for reference in pattern.findall(source.read_text(encoding='utf-8')):
                base = skill if source.is_relative_to(skill) and not reference.startswith('plugins/') else ROOT
                if not (base / reference).is_file():
                    missing.append(f'{name}: {reference}')
        self.assertEqual(missing, [])
