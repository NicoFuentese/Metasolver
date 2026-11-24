import os
import sys, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
lit = {}
with open(os.path.join(LIT, "mahvash_table1.csv"), newline="") as fh:
    for r in csv.DictReader(fh):
        lit[(int(r["class"]), int(r["n"]))] = {k: float(v) for k, v in r.items() if k not in ("class", "n")}
ro = camp(R22, "rot_orig"); rc = camp(R22, "rot_cls23")
print("ERROR rot_orig", [e for _, e in ro], "rot_cls23", [e for _, e in rc])
cf = ["Fast", "Balanced", "Quality"]
I1 = common([ro], [cf]); I2 = common([rc], [cf])
print("instancias", len(I1), len(I2))
def lit_tot(cls, key):
    return sum(v[key] for (c, n), v in lit.items() if c in cls) * 10
print("Literatura (x10): clases 1,4-8: LB %.0f CG %.0f HGAs %.0f BRKGA %.0f | clases 2,3: LB %.0f CG %.0f BRKGA %.0f | 8 clases CG %.0f BRKGA %.0f" % (
    lit_tot([1, 4, 5, 6, 7, 8], "LB"), lit_tot([1, 4, 5, 6, 7, 8], "CG"), lit_tot([1, 4, 5, 6, 7, 8], "HGAs"), lit_tot([1, 4, 5, 6, 7, 8], "BRKGA"),
    lit_tot([2, 3], "LB"), lit_tot([2, 3], "CG"), lit_tot([2, 3], "BRKGA"), lit_tot(range(1, 9), "CG"), lit_tot(range(1, 9), "BRKGA")))
print("CPU de Mahvash por instancia (promedio de celdas): clases 1,4-8 %.0f s, clases 2,3 %.0f s, 32 celdas %.0f s" % (
    np.mean([v["CPU"] for (c, n), v in lit.items() if c != 2 and c != 3]), np.mean([v["CPU"] for (c, n), v in lit.items() if c in (2, 3)]), np.mean([v["CPU"] for v in lit.values()])))
print("\n== con rotacion, 240 originales (clases 1,4-8), binario antiguo ==")
for c in cf: line(c + " rot", ro, c, I1)
print("== clases 2,3 ==")
for c in cf: line(c + " rot", rc, c, I2)
print("\n== comparaciones ==")
cmp(ro, "Balanced", ro, "Fast", I1, "1,4-8: Balanced - Fast"); cmp(ro, "Quality", ro, "Balanced", I1, "1,4-8: Quality - Balanced"); cmp(ro, "Quality", ro, "Fast", I1, "1,4-8: Quality - Fast")
cmp(rc, "Balanced", rc, "Fast", I2, "2,3: Balanced - Fast"); cmp(rc, "Quality", rc, "Balanced", I2, "2,3: Quality - Balanced"); cmp(rc, "Quality", rc, "Fast", I2, "2,3: Quality - Fast")
print("\n== frente a la literatura (suma de medias de semillas; x10 ya incluido) ==")
for c in cf:
    a = np.mean(tots(ro, c, I1)); b = np.mean(tots(rc, c, I2))
    print("  %-9s 1,4-8 %.1f (Mahvash CG %.0f: %+.1f; BRKGA %.0f: %+.1f; HGAs %.0f)  2,3 %.1f (CG %.0f: %+.1f; BRKGA %.0f: %+.1f)  8 clases %.1f (CG 9013: %+.1f; BRKGA 9009: %+.1f)" % (
        c, a, lit_tot([1, 4, 5, 6, 7, 8], "CG"), a - lit_tot([1, 4, 5, 6, 7, 8], "CG"), lit_tot([1, 4, 5, 6, 7, 8], "BRKGA"), a - lit_tot([1, 4, 5, 6, 7, 8], "BRKGA"), lit_tot([1, 4, 5, 6, 7, 8], "HGAs"),
        b, lit_tot([2, 3], "CG"), b - lit_tot([2, 3], "CG"), lit_tot([2, 3], "BRKGA"), b - lit_tot([2, 3], "BRKGA"), a + b, a + b - 9013, a + b - 9009))
print("\n== por celda frente a Mahvash CG (tolerancia 0.05 sobre el promedio por instancia) ==")
cells = collections.defaultdict(list)
for i in sorted(set(I1) | set(I2)):
    c, n, k = i[1:].split("_"); cells[(int(c), int(n))].append(i)
for c in cf:
    res = {"1,4-8": [0, 0, 0], "2,3": [0, 0, 0]}; resb = {"1,4-8": [0, 0, 0], "2,3": [0, 0, 0]}
    for (cl, n), ii in sorted(cells.items()):
        cp = rc if cl in (2, 3) else ro
        v = np.mean(tots(cp, c, ii)) / 10
        g = "2,3" if cl in (2, 3) else "1,4-8"
        d = v - lit[(cl, n)]["CG"]
        TOL = float(os.environ.get("TOL", "0.05"))
        res[g][0 if d < -TOL else 2 if d > TOL else 1] += 1
        db = v - lit[(cl, n)]["BRKGA"]
        resb[g][0 if db < -TOL else 2 if db > TOL else 1] += 1
    print("  %-9s vs CG (menor/igual/mayor): 1,4-8 %s  2,3 %s | vs BRKGA: 1,4-8 %s  2,3 %s" % (c, res["1,4-8"], res["2,3"], resb["1,4-8"], resb["2,3"]))
print("\n== celdas donde Quality rot queda por encima de Mahvash CG ==")
for (cl, n), ii in sorted(cells.items()):
    cp = rc if cl in (2, 3) else ro
    v = {c: np.mean(tots(cp, c, ii)) / 10 for c in cf}
    if v["Quality"] - lit[(cl, n)]["CG"] > 0.05 or v["Balanced"] - lit[(cl, n)]["CG"] > 0.05:
        print("  c%d n=%d  CG %.1f  Fast %.2f Balanced %.2f Quality %.2f  (LB %.1f)" % (cl, n, lit[(cl, n)]["CG"], v["Fast"], v["Balanced"], v["Quality"], lit[(cl, n)]["LB"]))
print("\n== MILP con rotacion ==")
for l, cp, I in [("1,4-8", ro, I1), ("2,3", rc, I2)]:
    for c in cf:
        n, imp, lp, pr, tm = milp_stats(cp, c, I)
        print("  %-6s %-9s n=%d mejoran %d (%.1f%%) LP prueba %d (%.1f%%) probado %d t_milp %.1f sin prueba %d" % (l, c, n, imp, 100 * imp / n, lp, 100 * lp / n, pr, tm, n - pr))
print("\n== exceso sobre la cota con rotacion (LB propio del solver) ==")
for l, cp, I in [("1,4-8", ro, I1), ("2,3", rc, I2)]:
    lb = sum(cp[0][0][i]["lb"] for i in I)
    print("  %s: LB del solver %d; " % (l, lb) + "; ".join("%s %.1f (+%.2f%%)" % (c, np.mean(tots(cp, c, I)), 100 * (np.mean(tots(cp, c, I)) / lb - 1)) for c in cf))
print("\n== tiempo medio por celda de n (Fast/Balanced/Quality) ==")
for n in (50, 100, 150, 200):
    ii = [i for i in I1 if i.split("_")[1] == str(n)]
    print("  n=%d  1,4-8: " % n + " ".join("%s %.1f" % (c, tmean(ro, c, ii)[0]) for c in cf))

