import os
from datetime import datetime
from typing import List, Dict
from .base import BaseReporter

class GroupedTXTReporter(BaseReporter):
    def __init__(self, output_file: str):
        self.output_file = output_file
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def report(self, results: List[Dict]):
        groups = {"Mükemmel Setup": [], "Güçlü Setup": [], "Orta Setup": [], "Zayıf Setup": []}
        for r in results:
            cat = r.get("category", "Zayıf Setup")
            groups.setdefault(cat, []).append(r)

        with open(self.output_file, "w") as f:
            f.write(f"MCSA Screener Report - {datetime.utcnow().isoformat()} UTC\n")
            f.write("= Summary by group =\n\n")
            for cat in ["Mükemmel Setup", "Güçlü Setup", "Orta Setup", "Zayıf Setup"]:
                f.write(f"-- {cat} ({len(groups.get(cat, []))}) --\n")
                for r in groups.get(cat, []):
                    f.write(f"{r['ticker']}: score={r['score']} comps={r['components']}\n")
                f.write("\n")
        return self.output_file
