"""Tabla por clase y tamano (apendice del paper): suma de las 10 instancias de cada celda, 8 clases, orientacion fija.
Columnas: cota inferior (cabeceras de los archivos de instancia), Mahvash et al. (CG), BRKGA, TS3, GVND, TS2P, GLS (Goncalves y Resende 2013, Tabla 8,
promedios x10) y Fast, Balanced y Quality (media de 3 semillas). Imprime el entorno tabular de LaTeX; las referencias salen de
literature/mahvash_table2.csv y problems/clp/benchs/MPV/literature_goncalves2013.csv. Las configuraciones de las clases 1,4-8 salen de las campanas
orig y quality, y las de las clases 2 y 3 de cls23_fixed."""
import os, sys, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

def read(path):
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        rd = csv.reader(l for l in fh if not l.startswith("#"))
        hdr = next(rd)
        return {(int(r[0]), int(r[1])): dict(zip(hdr, r)) for r in rd}
gon = read(os.path.join(REPO, "problems", "clp", "benchs", "MPV", "literature_goncalves2013.csv"))
mah = read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "literature", "mahvash_table2.csv"))
orig = camp(R11, "orig"); qual = camp(R11, "quality"); c23 = camp(R22, "cls23_fixed")

def lb_of(c, n):
    """suma de las cotas inferiores de la cabecera de las 10 instancias del archivo"""
    tot = 0
    with open(os.path.join(REPO, "problems", "clp", "benchs", "MPV", "original", "class%d" % c, "%d.txt" % n)) as fh:
        lines_ = fh.read().split("\n")
    i = 0
    for k in range(10):
        h = lines_[i].split(); tot += int(h[1])          # cabecera: k lb ub
        i += 2 + int(lines_[i + 1].split()[0])           # linea n W H D y n lineas de cajas
    return tot

def fmt(x):
    s = "%.1f" % x
    return s[:-2] if s.endswith(".0") else s

def mine(cp, cf, c, n):
    ii = [i for i in cp[0][0] if i.startswith("c%d_%d_" % (c, n))]
    return np.mean(tots(cp, cf, ii))

lines, tot = [], collections.defaultdict(float) if False else {}
import collections
tot = collections.defaultdict(float)
for c in (1, 2, 3, 4, 5, 6, 7, 8):
    for n in (50, 100, 150, 200):
        g = gon[(c, n)]
        lit = lambda k: (10 * float(g[k])) if g.get(k, "") != "" else None
        row = [c, n, lb_of(c, n), 10 * float(mah[(c, n)]["CG"]), lit("BRKGA_aNB"), lit("TS3"), lit("GVND"), lit("TS2P"), lit("GLS")]
        src = c23 if c in (2, 3) else orig
        mine_v = [mine(src, "Fast", c, n), mine(src, "Balanced", c, n), mine(qual if c not in (2, 3) else c23, "Quality", c, n)]
        vals = row[2:] + mine_v
        for k, v in enumerate(vals):
            if v is not None: tot[(c in (2, 3), k)] += v
        pub = [v for v in vals[1:7] if v is not None]      # Mahvash, BRKGA, TS3, GVND, TS2P, GLS
        best = min(pub)
        cells = []
        for k, v in enumerate(vals):
            s = "--" if v is None else fmt(v)
            if v is not None and 1 <= k <= 6 and abs(v - best) < 1e-9: s = r"\textbf{%s}" % s
            cells.append(s)
        lines.append(" & ".join([str(c), str(n)] + cells) + r" \\")
for key, label in ((False, "Total, classes 1 and 4--8"), (True, "Total, classes 2 and 3")):
    vals = [tot[(key, k)] for k in range(10)]
    # las columnas TS2P y GLS no existen para las clases 2 y 3
    s = [("--" if (key and k in (5, 6)) else fmt(vals[k])) for k in range(10)]
    lines.append(" & ".join([label, ""] + s) + r" \\")
print("\n".join(l for l in lines if l))
