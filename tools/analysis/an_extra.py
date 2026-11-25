"""Campanas extra: controles de squeaky wheel con rotacion y F4 con rotacion (rotctl, rotctl23), Quality con harvest (qharv) y escala MPV n=500/1000 (large).
Usa las semillas disponibles (archivo no vacio) y las instancias presentes en todas ellas, asi que tambien sirve con una campana a medias."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F403


def seeds_of(name):
    return tuple(s for s in (1, 2, 3) if os.path.exists(find("%s_s%d.csv" % (name, s))) and os.path.getsize(find("%s_s%d.csv" % (name, s))) > 0)


def get(name):
    ss = seeds_of(name)
    return camp(R22, name, ss), ss


def header(title, *parts):
    print("\n==", title, "|", "; ".join("%s: %d semillas" % (n, len(s)) for n, s in parts))


lit = {}
with open(os.path.join(LIT, "mahvash_table1.csv"), newline="") as fh:
    for r in csv.DictReader(fh):
        lit[(int(r["class"]), int(r["n"]))] = {k: float(v) for k, v in r.items() if k not in ("class", "n")}


def lit_tot(cls, key): return sum(v[key] for (c, n), v in lit.items() if c in cls) * 10


def rot_block(name, base, classes, pairs, ctl_cfgs):
    cp, s1 = get(name); bp, s2 = get(base)
    if not s1 or not s2: print("\n== %s: sin datos todavia" % name); return
    header("%s (rotacion) frente a %s" % (name, base), (name, s1), (base, s2))
    cfgs = ["F4rot"] + ctl_cfgs
    I = common([cp, bp], [cfgs, ["Fast", "Balanced", "Quality"]])
    print("instancias en comun:", len(I))
    if not I: return
    for c in cfgs: line(c, cp, c, I)
    for c in ["Fast", "Balanced", "Quality"]: line(c + " rot (" + base + ")", bp, c, I)
    print("-- controles a igual tiempo (A - B; negativo = A mejor)")
    for a, b, lab in pairs: cmp(bp, a, cp, b, I, lab)
    cmp(cp, "F4rot", bp, "Balanced", I, "F4 rot - Balanced rot")
    cmp(cp, "F4rot", bp, "Quality", I, "F4 rot - Quality rot")
    cmp(cp, "F4rot", cp, ctl_cfgs[1], I, "F4 rot - SWO (T~27-36)")
    full = len(I) == (240 if 2 not in classes else 80)
    if full:
        k = "CG"
        print("-- literatura (clases %s, completo): Mahvash CG %.0f; F4 rot %.1f (%+.1f); Quality rot %.1f" % (
            classes, lit_tot(classes, k), np.mean(tots(cp, "F4rot", I)), np.mean(tots(cp, "F4rot", I)) - lit_tot(classes, k), np.mean(tots(bp, "Quality", I))))
    n, imp, lp, pr, tm = milp_stats(cp, "F4rot", I)
    if n: print("  MILP de F4 rot: n=%d mejoran %d (%.1f%%) LP prueba %d probado %d t_milp %.1f sin prueba %d" % (n, imp, 100 * imp / n, lp, pr, tm, n - pr))


rot_block("rotctl", "rot_orig", (1, 4, 5, 6, 7, 8),
          [("Fast", "SwoT8rot", "Fast rot - SWO T=8"), ("Balanced", "SwoT27rot", "Balanced rot - SWO T=27"), ("Quality", "SwoT100rot", "Quality rot - SWO T=100")],
          ["SwoT8rot", "SwoT27rot", "SwoT100rot"])
rot_block("rotctl23", "rot_cls23", (2, 3),
          [("Fast", "SwoT12rot", "Fast rot - SWO T=12"), ("Balanced", "SwoT36rot", "Balanced rot - SWO T=36"), ("Quality", "SwoT120rot", "Quality rot - SWO T=120")],
          ["SwoT12rot", "SwoT36rot", "SwoT120rot"])

# --- Quality con harvest ---
qh, s1 = get("qharv"); q, s2 = get("quality")
if s1:
    header("Quality con harvest (-T 100 --harvest 10 --milp 100) frente a Quality", ("qharv", s1), ("quality", s2))
    I = common([qh, q], [["QualityHarvest"], ["Quality"]])
    print("instancias en comun:", len(I))
    line("Quality + harvest", qh, "QualityHarvest", I); line("Quality", q, "Quality", I)
    cmp(qh, "QualityHarvest", q, "Quality", I, "Quality+harvest - Quality")
    for l, cp, c in [("Quality + harvest", qh, "QualityHarvest"), ("Quality", q, "Quality")]:
        n, imp, lp, pr, tm = milp_stats(cp, c, I)
        print("  MILP %-18s n=%d mejoran %d (%.1f%%) LP prueba %d probado %d t_milp %.1f sin prueba %d" % (l, n, imp, 100 * imp / n, lp, pr, tm, n - pr))
else:
    print("\n== qharv: sin datos todavia")

# --- escala n=500/1000 ---
lg, s1 = get("large")
if s1:
    header("Escala MPV n=500/1000 (36 instancias nuevas; codigo nuevo)", ("large", s1))
    cf = ["Fast", "Balanced", "Quality", "SwoT26", "SwoT111"]
    I = common([lg], [cf])
    print("instancias:", len(I), " cota (suma):", sum(lg[0][0][i]["lb"] for i in I))
    for c in cf: line(c, lg, c, I)
    for a, b, lab in [("Fast", "SwoT26", "Fast - SWO T=26"), ("Balanced", "SwoT26", "Balanced - SWO T=26"), ("Quality", "SwoT111", "Quality - SWO T=111"),
                      ("Quality", "Balanced", "Quality - Balanced"), ("Balanced", "Fast", "Balanced - Fast")]:
        cmp(lg, a, lg, b, I, lab)
    for n in (500, 1000):
        ii = [i for i in I if i.split("_")[1] == str(n)]
        print("  n=%d (%d inst.): " % (n, len(ii)) + " ".join("%s %.1f" % (c, np.mean(tots(lg, c, ii))) for c in cf) + "  | LB %d" % sum(lg[0][0][i]["lb"] for i in ii))
    for c in ["Fast", "Balanced", "Quality"]:
        n, imp, lp, pr, tm = milp_stats(lg, c, I)
        print("  MILP %-9s n=%d mejoran %d (%.1f%%) LP prueba %d probado %d t_milp %.1f sin prueba %d" % (c, n, imp, 100 * imp / n, lp, pr, tm, n - pr))
else:
    print("\n== large: sin datos todavia")
