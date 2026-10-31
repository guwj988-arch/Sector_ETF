# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 21:49:01 2026

@author: kguke
"""


from pathlib import Path
from datetime import datetime
import re

site_folder = Path("site")
index_file = site_folder / "index.html"

# Find all dated prediction reports
reports = list(
    site_folder.glob("sector_predictions_????-??-??.html")
)

if not reports:
    raise RuntimeError("No prediction reports found.")

# Find the newest report based on its filename
def get_report_date(path):
    match = re.search(r"\d{4}-\d{2}-\d{2}", path.name)
    if not match:
        raise ValueError(f"Invalid report filename: {path.name}")
    return datetime.strptime(match.group(), "%Y-%m-%d")

latest = max(reports, key=get_report_date)

date_string = get_report_date(latest).strftime("%B %d, %Y")

# Read existing index.html
html = index_file.read_text(encoding="utf-8")

# Update report date
html, count1 = re.subn(
    r"Report date: .*?\. Open the interactive chart",
    f"Report date: {date_string}. Open the interactive chart",
    html
)

# Update chart link
html, count2 = re.subn(
    r'href="sector_predictions_\d{4}-\d{2}-\d{2}\.html"',
    f'href="{latest.name}"',
    html
)

if count1 != 1 or count2 != 1:
    raise RuntimeError("Could not update index.html correctly.")

# Save updated index
index_file.write_text(html, encoding="utf-8")

print("Latest report:", latest.name)
print("Report date:", date_string)
print("index.html updated successfully.")
