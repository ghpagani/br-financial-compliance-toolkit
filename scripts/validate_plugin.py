#!/usr/bin/env python3
"""Validate local plugin manifests, package references and tracked data files."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path('plugins/br-financial-compliance')
SKILL = PLUGIN / 'skills/br-financial-compliance'


def validate(root):
    def load(path):
        return json.loads((root / path).read_text(encoding='utf-8'))

    primary = load(PLUGIN / 'plugin.json')
    secondary = load(PLUGIN / '.claude-plugin/plugin.json')
    name, version = primary['name'], primary['version']
    if name != PLUGIN.name or primary != secondary:
        raise ValueError('Plugin manifests differ or name is invalid')
    source = (root / SKILL / 'scripts/review.py').read_text(encoding='utf-8')
    match = re.search(r"^VERSION\s*=\s*['\"]([^'\"]+)['\"]\s*$", source, re.MULTILINE)
    if not match or match.group(1) != version:
        raise ValueError('Engine version does not match plugin')
    for path in [Path('.claude-plugin/marketplace.json'), Path('.agents/plugins/marketplace.json')]:
        marketplace = load(path)
        entries = marketplace['plugins']
        if not isinstance(entries, list) or len(entries) != 1 or entries[0]['name'] != name:
            raise ValueError(f'Invalid marketplace entry: {path}')
        target = entries[0]['source']
        if isinstance(target, dict):
            if target.get('source') != 'local':
                raise ValueError('Marketplace source must be local')
            target = target['path']
        if not isinstance(target, str) or (root / target).resolve() != (root / PLUGIN).resolve():
            raise ValueError(f'Invalid marketplace path: {path}')
        if not (root / target / 'plugin.json').is_file():
            raise ValueError('Marketplace plugin is missing')
    for path in [PLUGIN / 'LICENSE', SKILL / 'LICENSE']:
        if not (root / path).is_file():
            raise ValueError(f'Missing {path}')
    for name in ['policy.json', 'expenses.csv', 'payroll.csv', 'budgets.csv']:
        if not (root / SKILL / 'examples' / name).is_file():
            raise ValueError(f'Missing example: {name}')
    skill_dir = root / SKILL
    skill_text = (skill_dir / 'SKILL.md').read_text(encoding='utf-8')
    front = re.match(r'\A---\s*\n(.*?)\n---\s*\n', skill_text, re.DOTALL)
    if not front or not re.search(r'^name:\s*br-financial-compliance\s*$', front.group(1), re.MULTILINE):
        raise ValueError('Invalid skill front matter name')
    if not re.search(r'^description:\s*\S.*$', front.group(1), re.MULTILINE):
        raise ValueError('Missing skill description')
    controls_text = (skill_dir / 'references/controls.md').read_text(encoding='utf-8')
    if f'# BR Financial Compliance Toolkit v{version}' not in skill_text.splitlines():
        raise ValueError('Skill heading version does not match plugin')
    if f'# Implemented controls v{version}' not in controls_text.splitlines():
        raise ValueError('Controls heading version does not match plugin')
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(PLUGIN).replace('\\', '/')], cwd=ROOT).decode('utf-8').split('\0')
    references = [SKILL / 'SKILL.md']
    for item in filter(None, tracked):
        path = Path(item)
        if path.suffix.lower() in {'.csv', '.json'} and not (path.is_relative_to(SKILL / 'examples') or path in {PLUGIN / 'plugin.json', PLUGIN / '.claude-plugin/plugin.json'}):
            raise ValueError(f'Unexpected tracked data file: {path}')
        if path.is_relative_to(SKILL / 'references') and path.suffix == '.md':
            references.append(path)
    pattern = re.compile(r'`((?:references|scripts|templates|examples)/[A-Za-z0-9_.\-/]+)`')
    for document in references:
        text = (root / document).read_text(encoding='utf-8')
        for reference in pattern.findall(text):
            target = (skill_dir / reference).resolve()
            if not target.is_relative_to(skill_dir.resolve()) or not target.is_file():
                raise ValueError(f'Missing skill reference: {reference}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        validate(args.root.resolve())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'Validation failed: {exc}', file=sys.stderr)
        return 1
    print('Plugin validation passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
