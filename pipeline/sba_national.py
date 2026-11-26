"""Nationwide SBA 7(a) loans for owner-run trades -> one JSON file per state + an index.
Inputs: the SBA FOIA 7(a) CSVs (FY2010-FY2019 and FY2020-Present) from https://data.sba.gov/dataset/7a-504-foia
Usage: python3 pipeline/sba_national.py <dir-with-csvs> <asof YYYY-MM-DD>
Output: data/sba/<ST>.json  {rows, stats}   and   data/sba/index.json
Row: [name, key, city, county, trade, date, amount, lender, termMonths, jobs, kind, status]
Privacy: sole proprietors' (BusinessType INDIVIDUAL) names are withheld; no street addresses are kept."""
import csv, json, re, statistics, sys, glob, os, collections
SRC, ASOF = sys.argv[1], sys.argv[2]
TRADES = {'238220': 'Plumbing & HVAC', '238210': 'Electrical', '238160': 'Roofing', '238320': 'Painting',
          '238330': 'Flooring', '238910': 'Excavation & site prep', '561730': 'Landscaping', '561710': 'Pest control',
          '561720': 'Janitorial', '811111': 'Auto repair', '811121': 'Auto body', '811192': 'Car washes'}
STATES = {'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California','CO':'Colorado','CT':'Connecticut','DE':'Delaware','DC':'District of Columbia','FL':'Florida','GA':'Georgia','HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming','PR':'Puerto Rico'}
SM = {'P I F': 'Paid in full', 'CHGOFF': 'Charged off', 'EXEMPT': 'Open', 'COMMIT': 'Approved, not yet funded', 'CANCLD': 'Canceled'}
def kind(a):
    if a == 'Change of Ownership': return 'Buyout'
    if a.startswith('Startup') or a.startswith('New'): return 'New business'
    if a.startswith('Existing') or a.startswith('Less than 3'): return 'Existing business'
    return 'Not reported'
def trade(naics, name):
    t = TRADES[naics]
    if naics != '238220': return t
    u = name.upper()
    hv = any(k in u for k in ['AIR', 'HEAT', 'HVAC', 'COOL', 'MECHANICAL', 'A/C', 'REFRIG', 'CLIMATE', 'COMFORT'])
    pl = any(k in u for k in ['PLUMB', 'DRAIN', 'SEWER', 'ROOTER', 'PIPE', 'WATER HEATER', 'LEAK'])
    return 'HVAC' if hv and not pl else ('Plumbing' if pl and not hv else t)
def nice(n):
    n = re.sub(r'\s+,', ',', n.strip()).rstrip('.').strip()
    if n.upper() == n: n = n.title().replace("'S ", "'s ").replace(' Llc', ' LLC').replace(' Dba ', ' dba ').replace(', Llc', ', LLC')
    return n
def key(n):
    u = re.sub(r'[^A-Z0-9 ]', ' ', n.upper()); u = re.sub(r'\b(LLC|INC|CORP|CORPORATION|CO|COMPANY|L L C|PA|LTD)\b', ' ', u)
    return ' '.join(u.split())
by = collections.defaultdict(list); i = 0
files = sorted(glob.glob(os.path.join(SRC, 'FOIA_7a_FY2010_FY2019_asof_*.csv')) + glob.glob(os.path.join(SRC, 'FOIA_7a_FY2020_Present_asof_*.csv')))
assert len(files) == 2, files
for f in files:
    for r in csv.DictReader(open(f, encoding='latin-1')):
        n = r['NaicsCode']; st = r['BorrState']
        if n not in TRADES or st not in STATES: continue
        i += 1; ind = r['BusinessType'] == 'INDIVIDUAL'
        by[st].append(['Sole proprietor (name withheld)' if ind else nice(r['BorrName']), ('IND' + str(i)) if ind else key(r['BorrName']),
            r['BorrCity'].strip().title(), r['ProjectCounty'].strip().title(), trade(n, r['BorrName']), r['ApprovalDate'],
            round(float(r['GrossApproval'] or 0)), nice(r['BankName']) if r['BankName'] else '', int(float(r['TermInMonths'] or 0)),
            int(float(r['JobsSupported'] or 0)), kind(r['BusinessAge']), SM.get(r['LoanStatus'], r['LoanStatus'])])
def stats(rows):
    funded = [o for o in rows if o[11] != 'Canceled']; bo = [o for o in funded if o[10] == 'Buyout']
    res = [o for o in rows if o[11] in ('Paid in full', 'Charged off') and o[5] < '2017-01-01']; co = sum(o[11] == 'Charged off' for o in res)
    return {'loans': len(rows), 'funded': len(funded), 'buyouts': len(bo), 'boMedian': statistics.median(o[6] for o in bo) if bo else 0,
            'boUnder1M': sum(o[6] < 1000000 for o in bo), 'res': len(res), 'pif': len(res) - co, 'co': co}
os.makedirs('data/sba', exist_ok=True); index = {'asof': ASOF, 'trades': sorted(set(TRADES.values()) | {'HVAC', 'Plumbing'}), 'naics': TRADES, 'states': {}}
allrows = []
for st, rows in sorted(by.items()):
    rows.sort(key=lambda x: x[5], reverse=True); allrows += rows
    json.dump({'state': st, 'asof': ASOF, 'rows': rows}, open(f'data/sba/{st}.json', 'w'), separators=(',', ':'))
    index['states'][st] = dict(name=STATES[st], **stats(rows))
index['national'] = stats(allrows)
json.dump(index, open('data/sba/index.json', 'w'), indent=1)
print('states', len(by), 'rows', len(allrows), index['national'])
