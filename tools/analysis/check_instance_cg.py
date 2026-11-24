"""Contrasta las instancias Instance_CG con lo que declara el articulo de Elhedhli, Gzara y Yildiz (2019): (1) distribuciones de sus Tablas 2 y 4
(proporciones d/w y h/w, repeticion, centroides por clase) y composicion por categorias de volumen de la Tabla 3; (2) la cota por volumen de cada instancia
frente a la cota L2 de las Tablas A.1-A.4 (literature/elhedhli_A.csv), celda por celda.
uso: python check_instance_cg.py [carpeta Instance_CG]   (por defecto $BPP_DATA/Instance_CG)"""
import os, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get('BPP_DATA', ''), 'Instance_CG')
import collections, math, os, re
import numpy as np
src = SRC
rows = collections.defaultdict(list)   # clase -> lista de (w,d,h,rep,tipo,n)
for n in (50, 100, 150, 200, 500, 1000, 1500, 2000):
    for fn in sorted(os.listdir(os.path.join(src, str(n)))):
        m = re.match(r"bin_pack_instance_i\((\d+)\)_c\((\d+)\)_s\(", fn)
        if not m: continue
        c = int(m.group(2))
        for ln in open(os.path.join(src, str(n), fn)):
            f = ln.split()
            if len(f) < 10: continue
            rows[c].append((int(f[0]), int(f[1]), int(f[2]), int(f[8]), f[7], n))
cats = [(2.72, 12.04), (12.05, 20.23), (20.28, 32.42), (32.44, 54.08), (54.31, 100.21)]
T3 = {1: [28.48, 58.75, 12.67, 0.1, 0], 2: [33.08, 32.36, 23.34, 7.94, 3.28], 3: [66.88, 24.75, 5.7, 2.6, 0.08], 4: [78.58, 13.16, 6.33, 1.78, 0.15]}
T4 = {1: (338.8, 232.81, 181.95, 13.72), 2: (336.89, 231.18, 180.51, 13.53), 3: (312.77, 215.31, 168, 10.97), 4: (304.86, 209.66, 164.87, 10.19)}
print("filas distintas por clase:", {c: len(v) for c, v in rows.items()}, " items totales:", {c: sum(r[3] for r in v) for c, v in rows.items()})
print("tipos:", collections.Counter(r[4] for v in rows.values() for r in v))
for c in (1, 2, 3, 4):
    R = np.array([(r[0], r[1], r[2], r[3]) for r in rows[c]], float)
    w, d, h, rep = R.T
    v = w * d * h / 1e6
    for label, wt in (("filas distintas", np.ones(len(v))), ("items (con repeticion)", rep)):
        cen = [np.average(x, weights=wt) for x in (w, d, h, v)]
        pc = []
        for lo, hi in cats:
            pc.append(100 * wt[(v >= lo - 0.03) & (v <= hi + 0.03)].sum() / wt.sum())
        pc_out = 100 * wt[(v < 2.7) | (v > 100.3)].sum() / wt.sum()
        print("clase %d  %-24s centroide (w,d,h,v) %s | %% por categoria %s (fuera de rango %.2f)" % (c, label, tuple(round(x, 2) for x in cen), [round(x, 2) for x in pc], pc_out))
    print("   Tabla 3 :", T3[c], "  Tabla 4 (generadas):", T4[c])
    rw = d / w; rh = h / w
    print("   d/w media %.3f sd %.3f (Tabla 2: normal 0.695, 0.118) | ln(h/w) media %.3f sd %.3f (lognormal -0.654, 0.453) | ln(rep) media %.3f sd %.3f (lognormal 0.544, 0.658)" % (
        rw.mean(), rw.std(), np.log(rh).mean(), np.log(rh).std(), np.log(rep).mean(), np.log(rep).std()))
    print("   w>=d en %.1f%% de las filas; w max %d, d max %d, h max %d; minimo w %d d %d h %d" % (100 * (w >= d).mean(), w.max(), d.max(), h.max(), w.min(), d.min(), h.min()))

print()
import csv, math
src = SRC
V = 1200 * 800 * 2055
mine = collections.defaultdict(list)
for n in (50, 100, 150, 200, 500, 1000, 1500, 2000):
    for fn in sorted(os.listdir(os.path.join(src, str(n)))):
        m = re.match(r"bin_pack_instance_i\((\d+)\)_c\((\d+)\)_s\(", fn)
        if not m: continue
        k, c = int(m.group(1)), int(m.group(2)); vol = 0
        for ln in open(os.path.join(src, str(n), fn)):
            f = ln.split()
            if len(f) >= 10: vol += int(f[0]) * int(f[1]) * int(f[2]) * int(f[8])
        mine[(c, n)].append((k, math.ceil(vol / V - 1e-9), vol / V))
lit = collections.defaultdict(list)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "literature", "elhedhli_A.csv")) as fh:
    for r in csv.DictReader(fh):
        lit[(int(r["class"]), int(r["n"]))].append((int(r["inst"]), float(r["lb_L2"]), int(r["bins"])))
same = diff = 0; bad = []
exact_order = 0
for key in sorted(mine):
    a = sorted(x[1] for x in mine[key]); b = sorted(int(x[1]) for x in lit[key])
    ok = a == b
    same += ok; diff += (not ok)
    if not ok: bad.append((key, a, b))
    # misma numeracion?
    ma = {x[0]: x[1] for x in mine[key]}; lb = {x[0]: int(x[1]) for x in lit[key]}
    exact_order += all(ma[i] == lb[i] for i in ma)
print("celdas (clase,n) con el mismo multiconjunto de cotas (volumen vs L2 del articulo): %d de %d" % (same, same + diff))
for k, a, b in bad: print("  celda %s: nuestra cota por volumen %s | L2 del articulo %s" % (k, a, b))
print("celdas con la misma cota en la misma numeracion de instancia (i): %d de 32" % exact_order)
# informativas: celdas n>=500 donde las 5 cotas no son todas iguales
for key in sorted(mine):
    if key[1] >= 500:
        s = sorted(set(x[1] for x in mine[key]))
        if len(s) > 1: print("  celda con cotas distintas entre instancias:", key, [(x[0], x[1]) for x in mine[key]], [(x[0], int(x[1])) for x in lit[key]])

