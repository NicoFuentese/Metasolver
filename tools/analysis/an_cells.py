import os
import sys, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
rows = []
with open(os.path.join(REPO, "problems", "clp", "benchs", "MPV", "literature_goncalves2013.csv"), newline="", encoding="utf-8", errors="replace") as fh:
    rd = csv.reader(l for l in fh if not l.startswith("#"))
    hdr = next(rd)
    for r in rd:
        rows.append(dict(zip(hdr, r)))
lit = {(int(r["class"]), int(r["n"])): r for r in rows}
orig = camp(R11, "orig"); qual = camp(R11, "quality"); c23 = camp(R22, "cls23_fixed")
sets = [("1,4-8", [("Fast", orig), ("Balanced", orig), ("Quality", qual)], None), ("2,3", [("Fast", c23), ("Balanced", c23), ("Quality", c23)], None)]
print("totales de la literatura (suma de promedios x10) sobre las celdas:", {k: round(10 * sum(float(r[k]) for (c, n), r in lit.items() if c in (1, 4, 5, 6, 7, 8) and r[k] != ""), 1) for k in ["BRKGA_aNB", "GVND", "TS2P", "GLS", "TS3"]})
for gname, cfgs, _ in sets:
    cls = (2, 3) if gname == "2,3" else (1, 4, 5, 6, 7, 8)
    print("\n== clases %s: celdas (media de 3 semillas / 10) frente a BRKGA_aNB, GVND, TS3 ==" % gname)
    tally = {c: [0, 0, 0] for c, _ in cfgs}
    for c in cls:
        for n in (50, 100, 150, 200):
            line_ = "  c%d n=%3d BRKGA %5.1f GVND %5.1f |" % (c, n, float(lit[(c, n)]["BRKGA_aNB"]), float(lit[(c, n)]["GVND"]))
            for cf, cp in cfgs:
                ii = [i for i in cp[0][0] if i.startswith("c%d_%d_" % (c, n))]
                v = np.mean(tots(cp, cf, ii)) / len(ii)
                d = v - float(lit[(c, n)]["BRKGA_aNB"])
                TOL = float(os.environ.get("TOL", "0.05"))
                tally[cf][0 if d < -TOL else 2 if d > TOL else 1] += 1
                line_ += " %s %5.2f" % (cf[:1], v)
            print(line_)
    for cf, _ in cfgs: print("  %s vs BRKGA (menor/igual/mayor): %s" % (cf, tally[cf]))

