"""Aggregate provincial reservation records without publishing individual trips."""
import argparse
import csv
import json
from bisect import bisect_left
from collections import Counter, defaultdict
from datetime import date, timezone, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://data.novascotia.ca/api/views/4zt7-x443/rows.csv?accessType=DOWNLOAD"


def metrics(hist):
    total = sum(hist.values())
    buckets = [0] * 5
    quantiles = []
    cumulative = 0
    for days, count in sorted(hist.items()):
        buckets[bisect_left((0, 7, 30, 90), days)] += count
        cumulative += count
        while len(quantiles) < 3 and cumulative * 4 >= total * (len(quantiles) + 1):
            quantiles.append(days)
    return [total, *quantiles, *buckets]


def parse_date(value):
    if "/" in value:
        month, day, year = map(int, value.split("/"))
        return date(year, month, day)
    return date.fromisoformat(value[:10])


def summarize(path):
    cells = defaultdict(Counter)
    records = included = 0
    years, parks = set(), set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            records += 1
            if row["BookingCategory"] != "Campsite" or row["TentOrRV"] not in ("Tent", "RV"):
                continue
            try:
                start = parse_date(row["ArrivalDate"])
                days = (start - parse_date(row["CreateDate"])).days
                nights = int(row["LengthOfStay(Nights)"])
            except (ValueError, TypeError):
                continue
            park = row["Park"].strip()
            if not park or days < 0 or nights < 1:
                continue
            included += 1
            parks.add(park)
            years.add(start.year)
            cells[(start.month, park, row["TentOrRV"], "weekend" if start.weekday() in (4, 5) else "weekday")][days] += 1
    if not included:
        raise ValueError("No usable overnight reservations")
    combined = defaultdict(Counter)
    for (month, park, kind, day), hist in cells.items():
        for m in (month, 0):
            for k in (kind, "all"):
                for d in (day, "all"):
                    combined[(m,park,k,d)].update(hist)
    months = defaultdict(dict)
    for (m,p,k,d), hist in sorted(combined.items()):
        months[m].setdefault(p, {})[f"{k}/{d}"] = metrics(hist)
    return months, dict(count=included, sourceRows=records, years=sorted(years), parks=sorted(parks), months=sorted(m for m in months if m))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--csv",type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as temp:
        path=args.csv or Path(temp)/"source.csv"
        if not args.csv:
            with urlopen(Request(SOURCE,headers={"User-Agent":"CoolCode CampCalendar/1.0"}),timeout=180) as response, path.open("wb") as out:
                shutil.copyfileobj(response,out)
        months, header = summarize(path)
        if header['sourceRows'] < 500000 or len(header['parks']) < 10:
            raise ValueError("Incomplete provincial export")
        header['retrieved']=datetime.now(timezone.utc).date().isoformat()
        dest=ROOT/"web/data"
        for m, rows in months.items():
            (dest/f"month-{m}.json").write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n')
        (dest/"status.json").write_text(json.dumps(header,ensure_ascii=False,indent=2)+'\n')
        print(f"{header['count']:,} overnight reservations from {len(header['parks'])} parks")

if __name__=="__main__":
    main()
