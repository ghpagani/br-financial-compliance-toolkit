import re
import contextlib
import io
import unittest
import unicodedata
from pathlib import Path

from test_review import ROOT, m


class MarkdownEscapeTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / 'plugins/br-financial-compliance/skills/br-financial-compliance/examples'
        self.policy = m.policy_load(base / 'policy.json')
        self.data = {kind: m.read_csv(base / f'{kind}.csv', kind)
                     for kind in ('expenses', 'payroll', 'budgets')}
        self.base_lines = len(m.markdown_report(m.review(**self.data, policy=self.policy, language='pt-BR')).splitlines())

    def verify_source(self, source, expected):
        report = m.review(**self.data, policy=dict(self.policy, source=source), language='pt-BR')
        text = m.markdown_report(report)
        self.assertEqual(len(text.splitlines()), self.base_lines)
        line = next(line for line in text.splitlines() if line.startswith('- Fonte: '))
        for fragment in expected:
            self.assertIn(fragment, line)
        raw = re.sub(r'&(?:#[0-9]+|[a-zA-Z]+);', '', line.split(': ', 1)[1].replace('`@`', ''))
        self.assertFalse(any(char in raw for char in ':/@.*_~#>!-+={}[]()`|$'))
        self.assertFalse(any(unicodedata.category(char) in ('Cf', 'Cc', 'Zl', 'Zp') for char in line))
        return line

    def test_line_paragraph_separators_and_math_dollar(self):
        # Found by Claude's independent probe after T-006b: U+2028/U+2029 split lines in some
        # viewers/scripts, and '$...$' is rendered as math by GitHub-flavored Markdown.
        self.verify_source('a b c\u0085d', ['a b c d'])
        self.verify_source('$x^2$ e $$y$$', ['&#36;x^2&#36; e &#36;&#36;y&#36;&#36;'])

    def test_scheme_url(self):
        self.verify_source('http://example.test/a', ['http&#58;&#47;&#47;example&#46;test&#47;a'])

    def test_www_url(self):
        self.verify_source('www.example.test', ['www&#46;example&#46;test'])

    def test_email(self):
        self.verify_source('example@example.test', ['example`@`example&#46;test'])

    def test_emphasis(self):
        self.verify_source('*strong*_word_~~strike~~', ['&#42;strong&#42;', '&#95;word&#95;', '&#126;&#126;strike&#126;&#126;'])

    def test_image(self):
        self.verify_source('![x](http://example.test)', ['&#33;&#91;x&#93;&#40;http&#58;&#47;&#47;'])

    def test_reference_link(self):
        self.verify_source('[ref]: http://example.test', ['&#91;ref&#93;&#58;', 'http&#58;&#47;&#47;'])

    def test_bidi_zero_width_and_control(self):
        self.verify_source('A\u202eB\u2066C\u200bD\nE\x00F', ['A B C D E F'])

    def test_literal_entity(self):
        self.verify_source('&#58; &lt; https://example.test', ['&amp;&#35;58;', '&amp;lt;', 'https&#58;&#47;&#47;'])

    def test_block_and_list_punctuation(self):
        self.verify_source('> # - + = {x} |', ['&gt;', '&#35;', '&#45;', '&#43;', '&#61;', '&#123;x&#125;', '&#124;'])

    def test_scope_portuguese_and_english_labels(self):
        portuguese = m.review(**self.data, policy=self.policy, language='pt-BR')
        self.assertIn('sobre fraude', portuguese['scope'])
        english = m.review(**self.data, policy=self.policy, language='en')
        text = m.markdown_report(english)
        self.assertIn('| Expense rows |', text)
        self.assertIn('| Processed expenses paid |', text)
        self.assertNotIn('| expense_rows |', text)

    def test_cli_help_describes_both_formats(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as error:
            m.main(['--help'])
        self.assertEqual(error.exception.code, 0)
        self.assertIn('New report file (JSON or Markdown); refuses overwrite', ' '.join(output.getvalue().split()))
