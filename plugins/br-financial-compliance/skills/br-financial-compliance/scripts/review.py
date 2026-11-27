#!/usr/bin/env python3
"""Local, read-only financial checks. No statutory tax/payroll calculations."""
import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path

VERSION = '0.1.0'
ZERO = Decimal('0.00')
CENT = Decimal('0.01')
FIELDS = {
    'expenses': 'id date project category vendor invoice gross paid currency document approval'.split(),
    'payroll': 'id period employee gross deductions net paid currency approval'.split(),
    'budgets': 'project category start end approved currency'.split(),
}


def money(value):
    # Explicit canonical input: no floats, exponents or locale ambiguity.
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,14}(?:\.[0-9]{1,2})?', value):
        raise ValueError('invalid monetary value: expected non-negative decimal string')
    return Decimal(value).quantize(CENT)


def iso(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('invalid ISO date')
    return date.fromisoformat(value)


def month(value):
    if not re.fullmatch(r'\d{4}-\d{2}', value or ''):
        raise ValueError('invalid competence YYYY-MM')
    return iso(value + '-01')


def token(value):
    # Opaque references, not CPF, names or account details. Pattern is not anonymization.
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,39}', value):
        raise ValueError('invalid reference; use opaque identifier')
    return value


def read_csv(path, kind):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)) or set(reader.fieldnames) != set(FIELDS[kind]):
            raise ValueError(f'{kind}: unexpected CSV header; consult data contract')
        rows = []
        for i, row in enumerate(reader, 2):
            if i > 100001:
                raise ValueError('row limit exceeded (100000)')
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f'{kind}: malformed row {i}')
            rows.append({k: v.strip() for k, v in row.items()})
        return rows


def policy_load(path):
    with open(path, encoding='utf-8') as f:
        p = json.load(f)
    required = {'version','effective_from','effective_to','currency','tolerance','require_document','require_approval','source'}
    if not isinstance(p, dict) or set(p) != required:
        raise ValueError('policy schema mismatch')
    token(p['version'])
    if iso(p['effective_from']) > iso(p['effective_to']):
        raise ValueError('invalid policy dates')
    if p['currency'] != 'BRL' or not isinstance(p['source'], str) or not p['source'].strip():
        raise ValueError('policy must specify BRL and a source')
    if any(type(p[k]) is not bool for k in ('require_document','require_approval')):
        raise ValueError('policy flags must be boolean')
    if money(p['tolerance']) > CENT:
        raise ValueError('tolerance above 0.01 not allowed in this version')
    return p


def review(expenses, payroll, budgets, policy):
    findings = []
    results = []
    start, end = iso(policy['effective_from']), iso(policy['effective_to'])
    tol = money(policy['tolerance'])
    spend = defaultdict(lambda: ZERO)
    budget_defs = defaultdict(list)
    eligible_expenses = []
    excluded_expense_rows = []
    def add(kind, row, code, severity, message, expected=None, actual=None):
        f = dict(module=kind, row=row, code=code, severity=severity, message=message, rule_version=policy['version'])
        if expected is not None:
            f.update(expected=str(expected), actual=str(actual), difference=str(actual-expected))
        findings.append(f)
    def invalid(kind, n, exc):
        # Do not include arbitrary input or exception text in reports.
        add(kind,n,'INPUT_INVALID','BLOCKER','Invalid, unsupported or out-of-period input; verify schema and coverage.')
    def common(r, day):
        if r['currency'] != policy['currency'] or not start <= day <= end:
            raise ValueError('out of scope')
    def flag_value(v):
        if v not in ('yes','no','unknown'):
            raise ValueError('invalid flag')
    for n,r in enumerate(budgets,2):
        try:
            key=(token(r['project']),token(r['category']))
            a,b=iso(r['start']),iso(r['end'])
            common(r,a); common(r,b)
            if a>b: raise ValueError('invalid dates')
            budget_defs[key].append((a,b,money(r['approved']),n))
        except (ValueError,TypeError,KeyError,InvalidOperation): invalid('budgets',n,None)
    overlaps=set()
    for key, defs in budget_defs.items():
        # Reject ambiguous matching periods rather than double-count.
        ordered=sorted(defs)
        max_end=None
        for a,b,limit,n in ordered:
            if max_end is not None and a<=max_end:
                overlaps.add(key)
                add('budgets',n,'BUDGET_OVERLAP','BLOCKER','Overlapping budget periods; matching disabled for this project/category.')
            max_end=b if max_end is None else max(max_end,b)
    ids=Counter(r.get('id') for r in expenses)
    payroll_ids=Counter(r.get('id') for r in payroll)
    invoice_groups=defaultdict(list)
    payroll_groups=defaultdict(list)
    for n,r in enumerate(expenses,2):
        try:
            token(r['id']); key=(token(r['project']),token(r['category']))
            vendor=token(r['vendor']); invoice=token(r['invoice'])
            day=iso(r['date']); common(r,day)
            gross,paid=money(r['gross']),money(r['paid'])
            flag_value(r['document']); flag_value(r['approval'])
            if ids[r['id']]>1: raise ValueError('duplicate row id')
            eligible_expenses.append((n,paid))
            invoice_groups[(vendor,invoice)].append(n)
            if abs(gross-paid)>tol:
                add('expenses',n,'EXP_PAYMENT_DIFF','REVIEW','Gross versus paid differs; verify retention, installments or credits.',gross,paid)
            if policy['require_document'] and r['document']!='yes':
                add('expenses',n,'EXP_DOCUMENT','REVIEW','Evidence not confirmed; request supporting document.')
            if policy['require_approval'] and r['approval']!='yes':
                add('expenses',n,'EXP_APPROVAL','REVIEW','Approval not confirmed; verify authorization.')
            matched=[(a,b,limit,j) for a,b,limit,j in budget_defs.get(key,[]) if a<=day<=b]
            if key in overlaps or len(matched)!=1:
                add('expenses',n,'EXP_BUDGET_UNMATCHED','REVIEW','No unique applicable budget; excluded from budget totals.')
            else:
                spend[matched[0][3]]+=paid
            results.append({'module':'expenses','row':n,'processed':True})
        except (ValueError,TypeError,KeyError,InvalidOperation):
            invalid('expenses',n,None); excluded_expense_rows.append(n); results.append({'module':'expenses','row':n,'processed':False})
    for group in invoice_groups.values():
        if len(group)>1:
            for n in group: add('expenses',n,'EXP_POSSIBLE_DUPLICATE','REVIEW','Repeated vendor/invoice reference; verify installments, splits or duplicate payment.')
    payroll_paid=[]
    for n,r in enumerate(payroll,2):
        try:
            token(r['id']); emp=token(r['employee']); day=month(r['period']); common(r,day)
            # Entire competence must be covered by policy.
            import calendar
            if date(day.year,day.month,calendar.monthrange(day.year,day.month)[1])>end: raise ValueError('partial competence')
            gross,deductions,net,paid=(money(r[k]) for k in ('gross','deductions','net','paid'))
            flag_value(r['approval'])
            if payroll_ids[r['id']]>1 or deductions>gross: raise ValueError('invalid payroll')
            payroll_paid.append(paid); payroll_groups[(emp,r['period'])].append(n)
            expected=gross-deductions
            if abs(expected-net)>tol: add('payroll',n,'PAY_NET_DIFF','REVIEW','Reported net differs from gross less reported deductions; not a statutory calculation.',expected,net)
            if abs(net-paid)>tol: add('payroll',n,'PAY_PAID_DIFF','REVIEW','Reported net versus paid differs; reconcile payment.',net,paid)
            if policy['require_approval'] and r['approval']!='yes': add('payroll',n,'PAY_APPROVAL','REVIEW','Approval not confirmed.')
            results.append({'module':'payroll','row':n,'processed':True})
        except (ValueError,TypeError,KeyError,InvalidOperation):
            invalid('payroll',n,None); results.append({'module':'payroll','row':n,'processed':False})
    for group in payroll_groups.values():
        if len(group)>1:
            for n in group: add('payroll',n,'PAY_REPEAT','REVIEW','Repeated employee/competence; verify separate payroll runs or duplicate payments.')
    budget_results=[]
    for key,defs in budget_defs.items():
        if key in overlaps: continue
        for a,b,limit,n in defs:
            actual=spend[n]
            budget_results.append({'row':n,'approved':str(limit),'matched_paid':str(actual),'remaining':str(limit-actual),'basis':'cash paid from supplied expense rows only'})
            if actual>limit+tol: add('budgets',n,'BUDGET_OVER','REVIEW','Matched cash payments exceed supplied budget.',limit,actual)
    counts=Counter(f['severity'] for f in findings)
    flagged={(f['module'],f['row']) for f in findings}
    for r in results:
        flags=(r['module'],r['row']) in flagged
        r['status']='NOT_PROCESSED' if not r['processed'] else ('REVIEW' if flags else 'NO_CONFIGURED_FINDING')
    return {'tool_version':VERSION,'policy_version':policy['version'],'policy_source':policy['source'],'policy_period':[str(start),str(end)],'currency':'BRL',
        'scope':'Arithmetic and supplied-policy checks only. No statutory, fraud or audit opinion.',
        'coverage':{'expense_rows':len(expenses),'expense_processed':len(eligible_expenses),'payroll_rows':len(payroll),'payroll_processed':len(payroll_paid),'budget_rows':len(budgets),'budget_evaluated':len(budget_results),'budget_unmatched_expenses':sum(f['code']=='EXP_BUDGET_UNMATCHED' for f in findings)},
        'totals':{'expense_paid_processed':str(sum((p for _,p in eligible_expenses),ZERO)),'payroll_paid_processed':str(sum(payroll_paid,ZERO)),'expense_paid_matched_to_budget':str(sum(spend.values(),ZERO))},
        'findings_by_severity':dict(counts),'findings':findings,'rows':results,'budgets':budget_results,
        'limitations':['Processed totals include flagged rows and exclude invalid rows; not certified totals.','Budget coverage is limited to supplied cash expense records; payroll is not included.','Input flags are assertions, not document authentication.','No bank reconciliation, legal tax rates, statutory payroll or payment execution.']}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy',required=True)
    for k in FIELDS: parser.add_argument('--'+k)
    parser.add_argument('--out',required=True,help='New JSON output; refuses overwrite')
    args=parser.parse_args(argv)
    if not any(getattr(args,k) for k in FIELDS): parser.error('provide at least one input CSV')
    try:
        p=policy_load(args.policy)
        data={k:read_csv(getattr(args,k),k) if getattr(args,k) else [] for k in FIELDS}
        with localcontext() as ctx:
            ctx.prec=40
            result=review(**data,policy=p)
        with open(args.out,'x',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
        print('Report generated locally. Review findings and coverage.')
        return 2 if result['findings_by_severity'].get('BLOCKER') else (1 if result['findings'] else 0)
    except (OSError,ValueError,TypeError,KeyError,InvalidOperation,csv.Error):
        print('Input/output error. Verify paths, schemas and policy; existing output is never overwritten.',file=sys.stderr)
        return 3

if __name__=='__main__': sys.exit(main())
