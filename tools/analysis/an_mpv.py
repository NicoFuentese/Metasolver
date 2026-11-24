import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

orig = camp(R11, "orig")            # Fast, Fastnh, Balanced (binario antiguo, 2026-11-11)
qual = camp(R11, "quality")         # Quality
ctl = camp(R22, "ctl")              # SwoT7, SwoT26, SwoT111
eq = camp(R22, "equiv_new")         # Fast, Balanced con el codigo nuevo
print("ERROR filas: orig", [e for _, e in orig], "quality", [e for _, e in qual], "ctl", [e for _, e in ctl], "equiv", [e for _, e in eq])
cfgs_o = [("Fast", "Fast"), ("Fastnh", "Fast sin harvest"), ("Balanced", "Balanced")]
I = common([orig, qual, ctl, eq], [["Fast", "Fastnh", "Balanced"], ["Quality"], ["SwoT7", "SwoT26", "SwoT111"], ["Fast", "Balanced"]])
print("instancias comunes", len(I))
print("\n== 240 originales, sin rotacion (binario antiguo) ==")
for c, l in cfgs_o: line(l, orig, c, I)
line("Quality", qual, "Quality", I)
for c in ["SwoT7", "SwoT26", "SwoT111"]: line("control " + c, ctl, c, I)
print("-- codigo nuevo (5c011841b) --")
line("Fast (nuevo)", eq, "Fast", I); line("Balanced (nuevo)", eq, "Balanced", I)
print("\n== comparaciones (A - B; negativo = A mejor) ==")
cmp(orig, "Fast", orig, "Fastnh", I, "harvest: Fast - Fast sin harv")
cmp(orig, "Balanced", orig, "Fast", I, "Balanced - Fast")
cmp(qual, "Quality", orig, "Balanced", I, "Quality - Balanced")
cmp(qual, "Quality", orig, "Fast", I, "Quality - Fast")
cmp(orig, "Fast", ctl, "SwoT7", I, "Fast - SWO T=7")
cmp(orig, "Balanced", ctl, "SwoT26", I, "Balanced - SWO T=26")
cmp(qual, "Quality", ctl, "SwoT111", I, "Quality - SWO T=111")
cmp(ctl, "SwoT26", ctl, "SwoT7", I, "SWO T26 - SWO T7")
cmp(ctl, "SwoT111", ctl, "SwoT26", I, "SWO T111 - SWO T26")
print("-- equivalencia codigo nuevo vs antiguo --")
cmp(eq, "Fast", orig, "Fast", I, "Fast nuevo - Fast antiguo")
cmp(eq, "Balanced", orig, "Balanced", I, "Balanced nuevo - Balanced antiguo")
for (dn, _), (do, _) in zip(eq, orig):
    same = sum(1 for i in I if dn[i]["Fast"]["bins"] == do[i]["Fast"]["bins"])
    same2 = sum(1 for i in I if dn[i]["Balanced"]["bins"] == do[i]["Balanced"]["bins"])
    print("   misma solucion en bins: Fast %d/240, Balanced %d/240" % (same, same2))
print("\n== MILP (n corridas, mejoran, LP prueba, probado, t_milp medio) ==")
for l, cp, c in [("Fast", orig, "Fast"), ("Fast sin harvest", orig, "Fastnh"), ("Balanced", orig, "Balanced"), ("Quality", qual, "Quality"),
                 ("Fast nuevo", eq, "Fast"), ("Balanced nuevo", eq, "Balanced")]:
    n, imp, lp, pr, tm = milp_stats(cp, c, I)
    print("  %-18s n=%d mejoran %d (%.1f%%) LP prueba %d (%.1f%%) probado %d (%.1f%%) t_milp %.1f s  sin prueba %d" % (l, n, imp, 100 * imp / n, lp, 100 * lp / n, pr, 100 * pr / n, tm, n - pr))
print("\n== por clase, media de semillas ==")
cl = {}
for i in I: cl.setdefault(int(i.split("_")[0][1:]), []).append(i)
print("  clase " + "".join("%8s" % k for k in ["Fast", "Fastnh", "Balanced", "Quality", "T7", "T26", "T111"]))
for k in sorted(cl):
    ii = cl[k]
    vals = [np.mean(tots(orig, "Fast", ii)), np.mean(tots(orig, "Fastnh", ii)), np.mean(tots(orig, "Balanced", ii)), np.mean(tots(qual, "Quality", ii)),
            np.mean(tots(ctl, "SwoT7", ii)), np.mean(tots(ctl, "SwoT26", ii)), np.mean(tots(ctl, "SwoT111", ii))]
    print("  c%d    " % k + "".join("%8.1f" % v for v in vals))

print("\n\n== clases 2,3 sin rotacion (cls23_fixed, binario antiguo) ==")
c23 = camp(R22, "cls23_fixed")
print("ERROR", [e for _, e in c23])
I2 = common([c23], [["Fast", "Balanced", "Quality"]])
print("instancias", len(I2))
for c in ["Fast", "Balanced", "Quality"]: line(c, c23, c, I2)
cmp(c23, "Balanced", c23, "Fast", I2, "Balanced - Fast"); cmp(c23, "Quality", c23, "Balanced", I2, "Quality - Balanced"); cmp(c23, "Quality", c23, "Fast", I2, "Quality - Fast")
for c in ["Fast", "Balanced", "Quality"]:
    n, imp, lp, pr, tm = milp_stats(c23, c, I2)
    print("  MILP %-9s n=%d mejoran %d  LP prueba %d  probado %d  t_milp %.1f" % (c, n, imp, lp, pr, tm))
print("  literatura clases 2,3: BRKGA 2519, GVND 2527, TS3 2543, Mahvash 2514 (=9766-7252)")
tt = {c: np.mean(tots(c23, c, I2)) for c in ["Fast", "Balanced", "Quality"]}
tot8 = {c: np.mean(tots(c23, c, I2)) + (np.mean(tots(orig, "Fast", I)) if c == "Fast" else np.mean(tots(orig, "Balanced", I)) if c == "Balanced" else np.mean(tots(qual, "Quality", I))) for c in tt}
print("  8 clases (1,4-8 + 2,3), media de semillas:", {c: round(v, 1) for c, v in tot8.items()}, " | Mahvash 9766, BRKGA 9777, SD 9795")

