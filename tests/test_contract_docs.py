import re
import unittest

from test_review import ROOT, m

SKILL = ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance'


class ContractDocsTests(unittest.TestCase):
    def test_documented_rejection_reasons_match_engine(self):
        # Both copies of the data contract must list exactly the engine's closed set of reasons.
        for path in (ROOT / 'docs/DATA-CONTRACT.md', SKILL / 'references/data-contract.md'):
            with self.subTest(path=path.name):
                text = path.read_text(encoding='utf-8')
                table = text.split('## Rejection reasons', 1)[1].split('Finding codes', 1)[0]
                documented = set(re.findall(r'^\| `([A-Z_]+)` \|', table, re.MULTILINE))
                self.assertEqual(documented, set(m.REASONS))

    def test_contract_copies_differ_only_in_policy_path(self):
        # The skill copy must stay in step with the repository copy (policy path is the one intended difference).
        repo = (ROOT / 'docs/DATA-CONTRACT.md').read_text(encoding='utf-8').replace('\r\n', '\n').splitlines()
        skill = (SKILL / 'references/data-contract.md').read_text(encoding='utf-8').replace('\r\n', '\n').splitlines()
        self.assertEqual(len(repo), len(skill))
        different = [i for i, (a, b) in enumerate(zip(repo, skill)) if a != b]
        self.assertEqual(len(different), 1)
        self.assertIn('examples/policy.json', repo[different[0]])
        self.assertIn('examples/policy.json', skill[different[0]])


if __name__ == '__main__':
    unittest.main()
