#!/usr/bin/env python3
"""Bitvavo-candles ophalen naar CSV. Gebruik:
   python3 fetch.py BTC-EUR 4h 4      (markt, interval, jaren)
"""
import csv, json, sys, time, urllib.request

market   = sys.argv[1] if len(sys.argv) > 1 else "BTC-EUR"
interval = sys.argv[2] if len(sys.argv) > 2 else "4h"
years    = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0

STEP = {"1h":3600,"4h":14400,"1d":86400}[interval] * 1000
end   = int(time.time()*1000)
start = end - int(years*365.25*86400*1000)
out   = f"{market}_{interval}.csv"
rows, cursor = {}, end

while cursor > start:
    url = (f"https://api.bitvavo.com/v2/{market}/candles"
           f"?interval={interval}&limit=1440&end={cursor}")
    with urllib.request.urlopen(url, timeout=15) as r:
        batch = json.load(r)
    if not batch:
        break
    for ts,o,h,l,c,v in batch:
        rows[int(ts)] = (int(ts),o,h,l,c,v)
    oldest = min(int(b[0]) for b in batch)
    print(f"  {len(batch):4d} candles t/m "
          f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(oldest/1000))}"
          f"  (totaal {len(rows)})")
    cursor = oldest - STEP
    if len(batch) < 2:
        break
    time.sleep(0.35)   # netjes binnen de rate limits blijven

with open(out,"w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp_ms","open","high","low","close","volume"])
    for ts in sorted(rows):
        w.writerow(rows[ts])
print(f"\nKlaar: {len(rows)} candles -> {out}")
