"""Florida DBPR construction license file -> active plumbing/HVAC businesses with first-licensed dates.
Input: CONSTRUCTIONLICENSE_1.csv from https://www2.myfloridalicense.com/construction-industry/public-records/
Columns (0-based): 1 occupation code, 2 licensee name, 3 DBA/business name, 8 city, 9 state, 11 county code,
13 primary status, 14 secondary status, 15 original licensure date, 17 expiration, 20 license number.
County codes 11-77 = Florida counties alphabetical, EXCEPT 65 St. Johns, 66 St. Lucie, 67 Santa Rosa, 68 Sarasota,
69 Seminole (verified against cities on Oct 28, 2026). Privacy: business names only; never output names/addresses.
Usage: python3 pipeline/fl_dbpr_extract.py CONSTRUCTIONLICENSE_1.csv"""
import csv, collections, json, datetime, sys
seq = ('Alachua Baker Bay Bradford Brevard Broward Calhoun Charlotte Citrus Clay Collier Columbia Miami-Dade DeSoto Dixie Duval '
       'Escambia Flagler Franklin Gadsden Gilchrist Glades Gulf Hamilton Hardee Hendry Hernando Highlands Hillsborough Holmes').split() + \
      ['Indian River'] + 'Jackson Jefferson Lafayette Lake Lee Leon Levy Liberty Madison Manatee Marion Martin Monroe Nassau Okaloosa Okeechobee Orange Osceola'.split() + \
      ['Palm Beach'] + 'Pasco Pinellas Polk Putnam'.split() + ['St. Johns', 'St. Lucie', 'Santa Rosa', 'Sarasota', 'Seminole'] + \
      'Sumter Suwannee Taylor Union Volusia Wakulla Walton Washington'.split()
C = {11 + i: n for i, n in enumerate(seq)}; assert len(C) == 67
T = {'CAC': 'HVAC', 'RA': 'HVAC', 'CMC': 'HVAC', 'RM': 'HVAC', 'CFC': 'Plumbing', 'RF': 'Plumbing'}
def d(s):
    try: return datetime.datetime.strptime(s, '%m/%d/%Y').date()
    except Exception: return None
rows = list(csv.reader(open(sys.argv[1], encoding='latin-1')))
act = [r for r in rows if r[1] in T and r[13] == 'C' and r[14] in ('A', '') and r[3].strip() and r[9] == 'FL' and r[11].isdigit() and int(r[11]) in C]
by = collections.defaultdict(list)
for r in act: by[(r[3].strip().upper().rstrip(' ,.'), T[r[1]])].append(r)
out = []
for (biz, tr), rs in by.items():
    rs2 = [r for r in rs if d(r[15])]
    if not rs2: continue
    r = min(rs2, key=lambda r: d(r[15]))
    out.append({'biz': biz, 'trade': tr, 'city': r[8].strip().title(), 'county': C[int(r[11])], 'first': d(r[15]).isoformat(),
                'holders': len({x[2] for x in rs}), 'lic': r[20], 'exp': r[17]})
json.dump({'asof': datetime.date.today().isoformat(), 'source': 'https://www2.myfloridalicense.com/sto/file_download/extracts//CONSTRUCTIONLICENSE_1.csv', 'rows': out},
          open('data/fl_dbpr_trades.json', 'w'))
print(len(out), 'active plumbing/HVAC businesses')
