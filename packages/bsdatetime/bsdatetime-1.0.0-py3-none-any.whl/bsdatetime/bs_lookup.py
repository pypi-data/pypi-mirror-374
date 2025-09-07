import csv, os
BS_YEARS = {}
csv_path = os.path.join(os.path.dirname(__file__), "data", "calendar_bs.csv")
with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        year = int(row[0])
        months = list(map(int, row[1:]))
        BS_YEARS[year] = months
