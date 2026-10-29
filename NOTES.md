# Next Owner (working name) — project notes

Free SBA-readiness check plus cited small-business deal records for individual buyers of owner-run
businesses (roughly under $1M a year in earnings, usually priced under $3M). Mission: help ordinary
people buy and keep owner-run businesses instead of seeing them rolled up.

**Status (Oct 28, 2026):** parked as a slow weekly build, Sunday sessions. Brand name NOT cleared:
"Bankable" has a live registered mark for small-business lending (Reg. 6604801, word disclaimed);
bankableowner.com was available. Keep a plain descriptive name until a lawyer clears one.

## Live site
- `index.html` (built output, served by GitHub Pages once enabled: Settings > Pages > Branch: main / root)
- Source: `source/site.dc.html` (template + logic). Rebuild: `python3 pipeline/build_site.py`
  (expects paths; adjust the two paths at the top if needed).

## Data sources (all public, all cited on the page)
| Section | Source | File | Refresh |
|---|---|---|---|
| Deal history | SBA 7(a) FOIA, data.sba.gov/dataset/7a-504-foia | `data/sba_fl_238220.json` via `pipeline/sba_extract.py` | quarterly (as-of 2026-06-30) |
| Long-established shops | FL DBPR construction licensee CSV | `data/fl_dbpr_trades.json` via `pipeline/fl_dbpr_extract.py` | monthly |
| For sale now | BizBuySell Insight Report (stats) + links out | hard-coded in source | quarterly |
| Readiness rules | SBA SOP 50 10 8.1 (eff. Oct 1, 2026), cross-checked via law-firm summary | hard-coded | when SBA updates |

Workspace network can't reach data.sba.gov or myfloridalicense.com: John downloads files in Chrome and
attaches them (or they're read from his Downloads folder).

## Key findings so far
- 968 FL plumbing/HVAC (NAICS 238220) 7(a) loans since FY2010; 852 funded; 100 buyouts since 2018
  ("Change of Ownership"); median buyout loan $815,650; 2010–2016 finished loans: 145 of 165 paid in full.
- Lake Area Heating and Air, LLC: $2.4M SBA buyout loan Dec 23, 2024 (Live Oak), LLC formed Sep 2024.
- 2,524 active FL plumbing/HVAC businesses whose license holder was first licensed in 2000 or earlier.

## Rules we hold to
- Every number cited to its source; gaps labeled (Not public / Not reported / Not yet matched / Licensed data).
- Business-level fields only. No owner names, no home addresses. Sole proprietors' names withheld.
- Readiness check runs only in the visitor's browser; nothing collected.
- Never call output a valuation, appraisal or advice. No brokering or success fees.

## Weekly roadmap (Sundays)
1. Nationwide deal history (all states, from the same SBA files) + state filter.
2. Texas licenses (TDLR) for "Long-established shops."
3. More trades: electrical, roofing, landscaping, etc. (NAICS codes).
4. Next state by buyout volume. Then: Excel download, sample brief, verify SOP against SBA PDF.
