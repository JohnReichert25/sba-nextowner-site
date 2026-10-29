"""Extract Florida plumbing/HVAC (NAICS 238220) SBA 7(a) loans from the SBA FOIA files.
Inputs: FOIA_7a_FY2010_FY2019_asof_*.csv and FOIA_7a_FY2020_Present_asof_*.csv
from https://data.sba.gov/dataset/7a-504-foia  (download in a browser; too large for git).
Usage: python3 pipeline/sba_extract.py <dir-with-csvs> [STATE] [NAICS]
Output: data/sba_<state>_<naics>.json  (rows + summary stats used by the site)."""
import csv, json, re, statistics, sys, glob, os
d = sys.argv[1]; ST = (sys.argv[2] if len(sys.argv) > 2 else 'FL'); NA = (sys.argv[3] if len(sys.argv) > 3 else '238220')
rows = []
for f in sorted(glob.glob(os.path.join(d, 'FOIA_7a_FY20*.csv'))):
    for r in csv.DictReader(open(f, encoding='latin-1')):
        if r['BorrState'] == ST and r['NaicsCode'] == NA: rows.append(r)
SM = {'P I F': 'Paid in full', 'CHGOFF': 'Charged off', 'EXEMPT': 'Open', 'COMMIT': 'Approved, not yet funded', 'CANCLD': 'Canceled'}
def kind(a):
    if a == 'Change of Ownership': return 'Buyout'
    if a.startswith('Startup') or a.startswith('New'): return 'New business'
    if a.startswith('Existing') or a.startswith('Less than 3'): return 'Existing business'
    return 'Not reported'
def trade(n):
    u = n.upper()
    hv = any(k in u for k in ['AIR', 'HEAT', 'HVAC', 'COOL', 'MECHANICAL', 'A/C', 'REFRIG', 'CLIMATE', 'COMFORT'])
    pl = any(k in u for k in ['PLUMB', 'DRAIN', 'SEWER', 'ROOTER', 'PIPE', 'WATER HEATER', 'LEAK'])
    return 'HVAC' if hv and not pl else ('Plumbing' if pl and not hv else 'Plumbing/HVAC')
def nice(n):
    n = re.sub(r'\s+,', ',', n.strip()).rstrip('.').strip()
    if n.upper() == n: n = n.title().replace("'S ", "'s ").replace(' Llc', ' LLC').replace(' Dba ', ' dba ').replace(', Llc', ', LLC')
    return n
def key(n):
    u = re.sub(r'[^A-Z0-9 ]', ' ', n.upper()); u = re.sub(r'\b(LLC|INC|CORP|CORPORATION|CO|COMPANY|L L C|PA|LTD)\b', ' ', u)
    return ' '.join(u.split())
out = []
for i, r in enumerate(rows):
    ind = r['BusinessType'] == 'INDIVIDUAL'   # privacy: withhold sole proprietors' names
    out.append(['Sole proprietor (name withheld)' if ind else nice(r['BorrName']), ('IND' + str(i)) if ind else key(r['BorrName']),
                r['BorrCity'].strip().title(), r['ProjectCounty'].strip().title(), trade(r['BorrName']), r['ApprovalDate'],
                round(float(r['GrossApproval'])), nice(r['BankName']) if r['BankName'] else '', int(float(r['TermInMonths'] or 0)),
                int(float(r['JobsSupported'] or 0)), kind(r['BusinessAge']), SM.get(r['LoanStatus'], r['LoanStatus'])])
out.sort(key=lambda x: x[5], reverse=True)
funded = [o for o in out if o[11] != 'Canceled']; bo = [o for o in funded if o[10] == 'Buyout']
res = [o for o in out if o[11] in ('Paid in full', 'Charged off') and o[5] < '2017-01-01']; co = sum(o[11] == 'Charged off' for o in res)
st = {'funded': len(funded), 'buyouts': len(bo), 'boMedian': statistics.median(o[6] for o in bo) if bo else 0,
      'res': len(res), 'pif': len(res) - co, 'co': co, 'boAmts': [o[6] for o in bo]}
p = f'data/sba_{ST.lower()}_{NA}.json'; json.dump({'rows': out, 'st': st}, open(p, 'w')); print(p, len(out), {k: v for k, v in st.items() if k != 'boAmts'})
