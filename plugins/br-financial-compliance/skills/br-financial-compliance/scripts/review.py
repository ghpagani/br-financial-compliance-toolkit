#!/usr/bin/env python3
"""Local, read-only financial checks. No statutory tax/payroll calculations."""
import argparse
import calendar
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from uuid import uuid4

VERSION = '0.1.0'
ZERO = Decimal('0.00')
CENT = Decimal('0.01')
FIELDS = {
    'expenses': 'id date project category vendor invoice gross paid currency document approval'.split(),
    'payroll': 'id period employee gross deductions net paid currency approval'.split(),
    'budgets': 'project category start end approved currency'.split(),
}
REASONS = frozenset({'HEADER', 'MALFORMED_ROW', 'DUPLICATE_ID', 'CURRENCY',
    'OUT_OF_PERIOD', 'PARTIAL_COMPETENCE', 'INVALID_DATE', 'INVALID_AMOUNT',
    'INVALID_REFERENCE', 'INVALID_FLAG', 'INVALID_PAYROLL', 'INVALID_BUDGET_DATES'})


class InputError(ValueError):
    def __init__(self, reason, field=None):
        if reason not in REASONS:
            raise ValueError('unsupported input reason')
        super().__init__(reason)
        self.reason = reason
        self.field = field


class CsvRow(dict):
    def __init__(self, values, line):
        super().__init__(values)
        self.line = line


def money(value, field=None):
    # Explicit canonical input: no floats, exponents or locale ambiguity.
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{1,14}(?:\.[0-9]{1,2})?', value):
        raise InputError('INVALID_AMOUNT', field)
    return Decimal(value).quantize(CENT)


def iso(value, field=None):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):
        raise InputError('INVALID_DATE', field)
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise InputError('INVALID_DATE', field) from None


def month(value, field=None):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}', value):
        raise InputError('INVALID_DATE', field)
    return iso(value + '-01', field)


def token(value, field=None):
    # Opaque references, not CPF, names or account details. Pattern is not anonymization.
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,39}', value):
        raise InputError('INVALID_REFERENCE', field)
    return value


def read_csv(path, kind):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f, strict=True)
        header = next(reader, None)
        if not header or len(header) != len(set(header)) or set(header) != set(FIELDS[kind]):
            raise ValueError(f'{kind}: unexpected CSV header; consult data contract')
        rows = []
        while True:
            start_line = reader.line_num + 1
            try:
                row = next(reader)
            except StopIteration:
                break
            if not row:
                continue
            if len(rows) >= 100000:
                raise ValueError('row limit exceeded (100000)')
            if len(row) != len(header):
                raise ValueError(f'{kind}: malformed row {start_line}')
            rows.append(CsvRow({k: v.strip() for k, v in zip(header, row)}, start_line))
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
    with localcontext() as ctx:
        ctx.prec = 40
        return _review(expenses, payroll, budgets, policy)


def _review(expenses, payroll, budgets, policy):
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
        findings[-1]['reason'] = exc.reason if isinstance(exc, InputError) else 'MALFORMED_ROW'
        if isinstance(exc, InputError) and exc.field is not None:
            findings[-1]['field'] = exc.field
    def common(r, day, field):
        if r['currency'] != policy['currency']:
            raise InputError('CURRENCY', 'currency')
        if not start <= day <= end:
            raise InputError('OUT_OF_PERIOD', field)
    def flag_value(v, field):
        if v not in ('yes','no','unknown'):
            raise InputError('INVALID_FLAG', field)
    for index,r in enumerate(budgets,2):
        n = getattr(r, 'line', index)
        try:
            key=(token(r['project'],'project'),token(r['category'],'category'))
            a,b=iso(r['start'],'start'),iso(r['end'],'end')
            common(r,a,'start'); common(r,b,'end')
            if a>b: raise InputError('INVALID_BUDGET_DATES')
            budget_defs[key].append((a,b,money(r['approved'],'approved'),n))
        except (ValueError,TypeError,KeyError,InvalidOperation) as exc: invalid('budgets',n,exc)
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
    amount_groups=defaultdict(list)
    payroll_groups=defaultdict(list)
    for index,r in enumerate(expenses,2):
        n = getattr(r, 'line', index)
        try:
            token(r['id'],'id'); key=(token(r['project'],'project'),token(r['category'],'category'))
            vendor=token(r['vendor'],'vendor'); invoice=token(r['invoice'],'invoice')
            day=iso(r['date'],'date'); common(r,day,'date')
            gross,paid=money(r['gross'],'gross'),money(r['paid'],'paid')
            flag_value(r['document'],'document'); flag_value(r['approval'],'approval')
            if ids[r['id']]>1: raise InputError('DUPLICATE_ID','id')
            eligible_expenses.append((n,paid))
            invoice_groups[(vendor,invoice)].append(n)
            amount_groups[(vendor,paid,day)].append((n,invoice))
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
        except (ValueError,TypeError,KeyError,InvalidOperation) as exc:
            invalid('expenses',n,exc); excluded_expense_rows.append(n); results.append({'module':'expenses','row':n,'processed':False})
    for group in invoice_groups.values():
        if len(group)>1:
            for n in group: add('expenses',n,'EXP_POSSIBLE_DUPLICATE','REVIEW','Repeated vendor/invoice reference; verify installments, splits or duplicate payment.')
    for group in amount_groups.values():
        if len({invoice for _, invoice in group}) > 1:
            for n, invoice in group:
                add('expenses',n,'EXP_POSSIBLE_DUPLICATE_AMOUNT','REVIEW','Same vendor, payment amount and date with different invoice references; verify installments, splits or duplicate payment.')
    payroll_paid=[]
    for index,r in enumerate(payroll,2):
        n = getattr(r, 'line', index)
        try:
            token(r['id'],'id'); emp=token(r['employee'],'employee'); day=month(r['period'],'period'); common(r,day,'period')
            # Entire competence must be covered by policy.
            if date(day.year,day.month,calendar.monthrange(day.year,day.month)[1])>end: raise InputError('PARTIAL_COMPETENCE','period')
            gross,deductions,net,paid=(money(r[k],k) for k in ('gross','deductions','net','paid'))
            flag_value(r['approval'],'approval')
            if payroll_ids[r['id']]>1: raise InputError('DUPLICATE_ID','id')
            if deductions>gross: raise InputError('INVALID_PAYROLL','deductions')
            payroll_paid.append(paid); payroll_groups[(emp,r['period'])].append(n)
            expected=gross-deductions
            if abs(expected-net)>tol: add('payroll',n,'PAY_NET_DIFF','REVIEW','Reported net differs from gross less reported deductions; not a statutory calculation.',expected,net)
            if abs(net-paid)>tol: add('payroll',n,'PAY_PAID_DIFF','REVIEW','Reported net versus paid differs; reconcile payment.',net,paid)
            if policy['require_approval'] and r['approval']!='yes': add('payroll',n,'PAY_APPROVAL','REVIEW','Approval not confirmed.')
            results.append({'module':'payroll','row':n,'processed':True})
        except (ValueError,TypeError,KeyError,InvalidOperation) as exc:
            invalid('payroll',n,exc); results.append({'module':'payroll','row':n,'processed':False})
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
        result=review(**data,policy=p)
        destination = Path(args.out)
        temporary = destination.parent / ('.brfc-' + uuid4().hex + '.tmp')
        created = False
        try:
            with temporary.open('x',encoding='utf-8') as f:
                created = True
                json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
            os.link(temporary, destination)
        finally:
            if created:
                os.unlink(temporary)
        print('Report generated locally. Review findings and coverage.')
        return 2 if result['findings_by_severity'].get('BLOCKER') else (1 if result['findings'] else 0)
    except (OSError,ValueError,TypeError,KeyError,InvalidOperation,csv.Error):
        print('Input/output error. Verify paths, schemas and policy; existing output is never overwritten.',file=sys.stderr)
        return 3

if __name__=='__main__': sys.exit(main())
