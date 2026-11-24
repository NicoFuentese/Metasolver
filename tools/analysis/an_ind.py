import os
import sys, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
L = collections.defaultdict(list)
with open(os.path.join(LIT, "elhedhli_A.csv"), newline="") as fh:
    for r in csv.DictReader(fh):
        L[(int(r["class"]), int(r["n"]))].append((float(r["bins"]), float(r["cpu"]), float(r["support_avg"]), float(r["items_supported_pct"])))
lc = {k: np.mean([x[0] for x in v]) for k, v in L.items()}
lt = {k: np.mean([x[1] for x in v]) for k, v in L.items()}
ls = {k: np.mean([x[2] for x in v]) for k, v in L.items()}
li = {k: np.mean([x[3] for x in v]) for k, v in L.items()}


def cellsum(ns): return sum(v for (c, n), v in lc.items() if n in ns)
def run(name, ns, cfgs, labels):
    cp = camp(IND, name)
    print("\n=====", name, "ERROR", [e for _, e in cp])
    I = common([cp], [cfgs]); print("instancias", len(I))
    for c in cfgs: line(labels.get(c, c), cp, c, I)
    lb = sum(cp[0][0][i]["lb"] for i in I)
    print("  cota del solver (suma) %d; LCGA (suma de promedios por celda x5, mismas celdas) %.1f; tiempo CPU medio LCGA %.0f s; soporte medio LCGA %.1f%%, cajas con >=70%% %.1f%%" % (
        lb, cellsum(ns) * 5, np.mean([v for (c, n), v in lt.items() if n in ns]), np.mean([v for (c, n), v in ls.items() if n in ns]), np.mean([v for (c, n), v in li.items() if n in ns])))
    cells = collections.defaultdict(list)
    for i in I:
        c, n, k = i[1:].split("_"); cells[(int(c), int(n))].append(i)
    print("  celda por celda (media de 5 inst. y 3 semillas) vs LCGA: " + " ".join("%s" % c for c in cfgs))
    summ = {c: [0, 0, 0] for c in cfgs}
    for key in sorted(cells):
        ii = cells[key]
        vals = {c: np.mean(tots(cp, c, ii)) / len(ii) for c in cfgs}
        for c in cfgs:
            d = vals[c] - lc[key]
            summ[c][0 if d < -0.05 else 2 if d > 0.05 else 1] += 1
    for c in cfgs:
        t = tots(cp, c, I)
        print("  %-10s total medio %7.1f (%+.1f vs LCGA = %.1f, %+.1f%%)  celdas menor/igual/mayor %s" % (c, np.mean(t), np.mean(t) - cellsum(ns) * 5, cellsum(ns) * 5, 100 * (np.mean(t) / (cellsum(ns) * 5) - 1), summ[c]))
    return cp, I


big, Ib = run("ind_large", [500, 1000, 1500, 2000], ["C2", "S02", "S05", "P02", "P05", "S05_60", "P05_60"],
              {"C2": "construccion k=1 t=2", "S02": "SWO T=18 t=0.2", "S05": "SWO T=18 t=0.5", "P02": "SWO+harv+partic T=18 t=0.2", "P05": "SWO+harv+partic T=18 t=0.5", "S05_60": "SWO T=60 t=0.5", "P05_60": "SWO+harv+partic T=60 t=0.5"})
print("-- comparaciones (A - B) ind_large --")
cmp(big, "P02", big, "S02", Ib, "particion: P02 - S02"); cmp(big, "P05", big, "S05", Ib, "particion: P05 - S05"); cmp(big, "P05_60", big, "S05_60", Ib, "particion: P05_60 - S05_60")
cmp(big, "S05", big, "C2", Ib, "SWO S05 - construccion C2"); cmp(big, "S02", big, "C2", Ib, "SWO S02 - C2"); cmp(big, "P05", big, "C2", Ib, "P05 - C2"); cmp(big, "P05_60", big, "C2", Ib, "P05_60 - C2"); cmp(big, "S05_60", big, "S05", Ib, "S05_60 - S05")
for c in ["P02", "P05", "P05_60"]:
    n, imp, lp, pr, tm = milp_stats(big, c, Ib); print("  MILP %-7s n=%d mejoran %d LP prueba %d probado %d t_milp %.1f" % (c, n, imp, lp, pr, tm))
print("  por n (suma de bins, media de semillas): n:", [500, 1000, 1500, 2000])
for c in ["C2", "S05", "P05", "P05_60"]:
    print("   %-7s " % c + " ".join("%7.1f" % np.mean(tots(big, c, [i for i in Ib if i.split("_")[1] == str(n)])) for n in (500, 1000, 1500, 2000)) + "   t medio por n " + " ".join("%6.1f" % tmean(big, c, [i for i in Ib if i.split("_")[1] == str(n)])[0] for n in (500, 1000, 1500, 2000)))
sm, Is = run("ind_small", [50, 100, 150, 200], ["Imp", "C2", "S05", "P05"], {"Imp": "fase de mejora T=30", "C2": "construccion k=1 t=2", "S05": "SWO T=10 t=0.5", "P05": "SWO+harv+partic T=10 t=0.5"})
print("-- comparaciones ind_small --")
cmp(sm, "P05", sm, "S05", Is, "particion: P05 - S05"); cmp(sm, "S05", sm, "C2", Is, "S05 - C2"); cmp(sm, "Imp", sm, "C2", Is, "Imp - C2"); cmp(sm, "P05", sm, "Imp", Is, "P05 - Imp"); cmp(sm, "S05", sm, "Imp", Is, "S05 - Imp"); cmp(sm, "P05", sm, "C2", Is, "P05 - C2")
for c in ["P05"]:
    n, imp, lp, pr, tm = milp_stats(sm, c, Is); print("  MILP %-5s n=%d mejoran %d LP prueba %d probado %d t_milp %.2f" % (c, n, imp, lp, pr, tm))

