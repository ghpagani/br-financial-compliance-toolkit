#!/usr/bin/env python3
"""Build deterministic ZIPs with a br-financial-compliance/ top-level directory."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path('plugins/br-financial-compliance')
SKILL = PLUGIN / 'skills/br-financial-compliance'


def version():
    primary = json.loads((ROOT / PLUGIN / 'plugin.json').read_text(encoding='utf-8'))
    other = json.loads((ROOT / PLUGIN / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
    source = (ROOT / SKILL / 'scripts/review.py').read_text(encoding='utf-8')
    match = re.search(r"^VERSION\s*=\s*['\"]([^'\"]+)['\"]\s*$", source, re.MULTILINE)
    value = primary.get('version')
    if (primary != other or not match or value != match.group(1) or
            not isinstance(value, str) or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', value)):
        raise ValueError('Plugin and engine versions or manifests do not match')
    return value


def tracked_files():
    data = subprocess.check_output(['git', 'ls-files', '-z', '--', str(PLUGIN).replace('\\', '/')], cwd=ROOT)
    paths = [Path(item) for item in data.decode('utf-8').split('\0') if item]
    return sorted((p for p in paths if '__pycache__' not in p.parts and p.suffix != '.pyc'
                   and 'reports' not in p.parts and not p.name.startswith('demo-report')), key=lambda p: p.as_posix())


def write_archive(stream, files, base):
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            if not path.is_relative_to(base):
                continue
            data = (ROOT / path).read_bytes()
            if path.suffix.lower() in {'.md', '.json', '.py', '.csv', '.txt'} or path.name == 'LICENSE':
                data = data.replace(b'\r\n', b'\n')
            info = zipfile.ZipInfo('br-financial-compliance/' + path.relative_to(base).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    created = []
    try:
        ver = version()
        files = tracked_files()
        if not files:
            raise ValueError('No tracked plugin files found')
        args.out_dir.mkdir(parents=True, exist_ok=True)
        targets = [(args.out_dir / f'br-financial-compliance-skill-{ver}.zip', SKILL),
                   (args.out_dir / f'br-financial-compliance-plugin-{ver}.zip', PLUGIN)]
        checksum = args.out_dir / 'SHA256SUMS'
        if any(path.exists() for path, _ in targets) or checksum.exists():
            raise FileExistsError('Output already exists')
        for path, base in targets:
            with path.open('xb') as stream:
                created.append(path)
                write_archive(stream, files, base)
        with checksum.open('x', encoding='utf-8', newline='\n') as stream:
            created.append(checksum)
            for path, _ in targets:
                stream.write(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n')
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        print(f'Build failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
