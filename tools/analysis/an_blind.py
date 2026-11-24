import os
import sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

b = camp(R11, "blind2rep")
print("ERROR:", [e for _, e in b])
cf = ["Fast", "FastNoHarvest", "Balanced", "BalancedPlain", "SwoT26"]
I = common([b], [cf])
print("instancias:", len(I), " LB (suma):", sum(b[0][0][i]["lb"] for i in I))
lab = {"Fast": "Fast", "FastNoHarvest": "Fast sin harvest", "Balanced": "Balanced", "BalancedPlain": "Balanced con MILP simple", "SwoT26": "SWO solo T=26"}
for c in cf: line(lab[c], b, c, I)
print("-- comparaciones --")
cmp(b, "Fast", b, "FastNoHarvest", I, "Fast - Fast sin harvest")
cmp(b, "Fast", b, "SwoT26", I, "Fast - SWO T=26")
cmp(b, "Balanced", b, "SwoT26", I, "Balanced - SWO T=26")
cmp(b, "Balanced", b, "Fast", I, "Balanced - Fast")
cmp(b, "BalancedPlain", b, "Balanced", I, "MILP simple - MILP con objetivo")
cmp(b, "FastNoHarvest", b, "SwoT26", I, "Fast sin harvest - SWO T=26")
print("-- MILP --")
def tm_sum(cp, c):
    s = 0.0; n = 0
    for d, _ in cp:
        for i in I:
            m = re.search(r"t_milp (\S+)", d[i][c]["milp"])
            if m: s += float(m.group(1)); n += 1
    return s, n
for c in ["Fast", "FastNoHarvest", "Balanced", "BalancedPlain"]:
    n, imp, lp, pr, tm = milp_stats(b, c, I)
    s, k = tm_sum(b, c)
    print("  %-14s n=%d mejoran %d (%.1f%%) LP prueba %d (%.1f%%) probado %d (%.1f%%) sin prueba %d  t_milp medio %.2f s, total por semilla %.0f s" % (c, n, imp, 100 * imp / n, lp, 100 * lp / n, pr, 100 * pr / n, n - pr, tm, s / 3))
# columnas / kept en las corridas donde corrio el MILP (kept > 0)
for c in ["Balanced", "BalancedPlain", "Fast"]:
    ratios = []; cols = []
    for d, _ in b:
        for i in I:
            m = re.search(r"cols (\d+).*kept (\d+)", d[i][c]["milp"])
            if m and int(m.group(2)) > 0:
                cols.append(int(m.group(1))); ratios.append(int(m.group(2)) / int(m.group(1)))
    if ratios: print("  %-14s corridas con MILP resuelto (kept>0): %d, columnas medias %.0f, kept/cols medio %.1f%% (mediana %.1f%%)" % (c, len(ratios), np.mean(cols), 100 * np.mean(ratios), 100 * np.median(ratios)))
# cota LP del pool
for c in ["Balanced", "Fast"]:
    eq = plus = lt = 0; sumceil = []
    for d, _ in b[:1]:
        sc = 0
        for i in I:
            m = re.search(r"bins (\d+) .* lp (\S+) kept", d[i][c]["milp"]);
            if not m: continue
            bins = int(m.group(1)); z = float(m.group(2)); ce = math.ceil(z - 1e-6); sc += ce
            if bins == ce: eq += 1
            elif bins == ce + 1: plus += 1
            else: lt += 1
        print("  semilla 1 %s: bins == ceil(LP) en %d, bins = ceil(LP)+1 en %d, otros %d; suma de ceil(LP) %d vs bins %d" % (c, eq, plus, lt, sc, sum(d[i][c]["bins"] for i in I)))
# por clase
cls = collections.defaultdict(list) if False else {}
for i in I:
    cls.setdefault(i.split("_")[0], []).append(i)
print("  por clase (media de semillas):  clase " + " ".join("%8s" % c for c in cf))
for k in sorted(cls):
    print("   %s " % k + " ".join("%8.1f" % np.mean(tots(b, c, cls[k])) for c in cf))

