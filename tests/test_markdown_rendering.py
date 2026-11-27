import unittest

from test_review import ROOT, m


class MarkdownRenderingTests(unittest.TestCase):
    def test_email_delimiter_is_an_inert_code_span(self):
        base = ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples'
        policy = dict(m.policy_load(base / 'policy.json'), source='x@example.test `code`\n<script>')
        report = m.review([], [], [], policy, language='en')
        source_line = next(line for line in m.markdown_report(report).splitlines() if line.startswith('- Source: '))
        rendered_source = source_line.removeprefix('- Source: ')
        self.assertIn('x`@`example&#46;test', rendered_source)
        self.assertEqual(rendered_source.count('`'), 2)
