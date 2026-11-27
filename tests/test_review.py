import importlib.util
import unittest
from pathlib import Path
from support import temporary_directory
import json

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'plugins/br-financial-compliance/skills/br-financial-compliance/scripts/review.py'
spec=importlib.util.spec_from_file_location('review',PATH)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class ReviewTests(unittest.TestCase):
    def test_temporary_directory_helper(self):
        with temporary_directory() as directory:
            path = Path(directory)
            self.assertTrue(path.is_dir())
            (path / 'synthetic.txt').write_text('synthetic', encoding='utf-8')
        self.assertFalse(path.exists())

    def setUp(self):
        self.p=m.policy_load(ROOT/'examples/policy.json')
        self.e=m.read_csv(ROOT/'examples/expenses.csv','expenses')
        self.y=m.read_csv(ROOT/'examples/payroll.csv','payroll')
        self.b=m.read_csv(ROOT/'examples/budgets.csv','budgets')
    def run_review(self): return m.review(self.e,self.y,self.b,self.p)
    def codes(self): return [f['code'] for f in self.run_review()['findings']]
    def test_decimal(self): self.assertEqual(str(m.money('0.1')+m.money('0.2')),'0.30')
    def test_invalid_money(self):
        for x in ['-1','1,00','1e3','NaN','1.001',1.0]:
            with self.subTest(x=x),self.assertRaises(ValueError): m.money(x)
    def test_demo_totals(self):
        r=self.run_review(); self.assertEqual(r['totals'],{'expense_paid_processed':'2850.00','payroll_paid_processed':'9000.00','expense_paid_matched_to_budget':'2650.00'}); self.assertEqual(r['coverage']['budget_unmatched_expenses'],1)
    def test_duplicate(self): self.assertEqual(self.codes().count('EXP_POSSIBLE_DUPLICATE'),2)
    def test_expense_flags(self):
        for c in ['EXP_PAYMENT_DIFF','EXP_DOCUMENT','EXP_APPROVAL','EXP_BUDGET_UNMATCHED','BUDGET_OVER']: self.assertIn(c,self.codes())
    def test_payroll_flags(self):
        for c in ['PAY_NET_DIFF','PAY_PAID_DIFF','PAY_APPROVAL']: self.assertIn(c,self.codes())
    def test_invalid_currency_excluded(self):
        self.e[0]['currency']='USD'; r=self.run_review(); self.assertEqual(r['coverage']['expense_processed'],4); self.assertIn('INPUT_INVALID',self.codes()); self.assertEqual(r['totals']['expense_paid_processed'],'1850.00')
    def test_duplicate_id_excluded(self):
        self.e[1]['id']=self.e[0]['id']; self.assertEqual(self.run_review()['coverage']['expense_processed'],3)
    def test_budget_overlap(self):
        self.b.append(dict(self.b[0])); self.assertIn('BUDGET_OVERLAP',self.codes()); self.assertEqual(self.run_review()['totals']['expense_paid_matched_to_budget'],'650.00')
    def test_payroll_partial_period(self):
        self.p['effective_to']='2026-11-15'; self.assertEqual(self.run_review()['coverage']['payroll_processed'],0)
    def test_tolerance(self):
        self.e[0]['paid']='999.99'; self.assertFalse(any(f['row']==2 and f['code']=='EXP_PAYMENT_DIFF' for f in self.run_review()['findings']))
    def test_no_budgets(self):
        self.b=[]; self.assertEqual(self.run_review()['coverage']['budget_unmatched_expenses'],5)
    def test_invalid_schema(self):
        with temporary_directory() as d:
            p=Path(d)/'x.csv'; p.write_text('id,unknown\n1,2\n');
            with self.assertRaises(ValueError): m.read_csv(p,'expenses')
    def test_policy_explicit(self):
        with temporary_directory() as d:
            p=Path(d)/'p.json'; self.p['require_document']='false'; p.write_text(json.dumps(self.p));
            with self.assertRaises(ValueError): m.policy_load(p)
    def test_no_overwrite(self):
        with temporary_directory() as d:
            p=Path(d)/'out.json'; p.write_text('original'); args=['--policy',str(ROOT/'examples/policy.json'),'--expenses',str(ROOT/'examples/expenses.csv'),'--out',str(p)]; self.assertEqual(m.main(args),3); self.assertEqual(p.read_text(),'original')
    def test_clean_row(self):
        self.e=[self.e[-1]];self.y=[self.y[0]];r=self.run_review();self.assertFalse(r['findings']);self.assertTrue(all(x['status']=='NO_CONFIGURED_FINDING' for x in r['rows']))

if __name__=='__main__': unittest.main()
